from app.utils.database import alarms_collection, alarms_payload_collection
from app.utils.alarm_types import ALARM_TYPE_DESCRIPTIONS, ALARMS_GAUSS_MAPPING
from app.models.alarm_data import AlarmPayload
from app.services.gauss_service import send_alarms_to_gauss
import os
from datetime import datetime, timezone
from typing import List, Optional

LOG_ALARM_PAYLOAD = os.getenv("LOG_ALARM_PAYLOAD", "false").lower() == 'true'
LOG_ALARM_DATA = os.getenv("LOG_ALARM_DATA", "false").lower() == 'true'

alarm_cache = {}


async def process_alarm_data(payload: AlarmPayload):
    try:
        if LOG_ALARM_DATA:
            for alarm_data in payload.data:
                document = alarm_data.dict()
                await alarms_collection.insert_one(document)
                print(f"Saved Alarm data for vehicle {alarm_data.vehicleId}")

        if LOG_ALARM_PAYLOAD:
            payload_doc = {
                "tenantId": payload.tenantId,
                "type": payload.type,
                "time": payload.time,
                "receivedAt": datetime.now(timezone.utc),
                "dataCount": len(payload.data),
                "data": [alarm_data.dict() for alarm_data in payload.data]
            }
            await alarms_payload_collection.insert_one(payload_doc)
            print("Saved entire ALARM payload document.")

        for alarm_data in payload.data:
            await handle_alarm_for_gauss(alarm_data)
        return {
            "status": "success",
            "message": "ALARM data processed successfully"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_alarms_data(
        vehicle_number: Optional[str] = None,
        start_time: Optional[str] = None) -> List[dict]:
    """
    Get all alarms data. Optionally filter by vehicle number.
    """
    match_filter = {
        'type': 'ALARM'
    }
    if vehicle_number:
        match_filter['data.vehicleNumber'] = vehicle_number
    if start_time:
        match_filter['time'] = {'$gt': start_time}

    aggregation_pipeline = [
        {
            '$match': match_filter
        },
        {
            '$sort': {
                'time': -1
            }
        }, {
            '$unwind': {
                'path': '$data'
            }
        }, {
            '$project': {
                '_id': '$_id',
                'alarmCode': '$data.alarmType',
                'vehicleNumber': '$data.vehicleNumber',
                'time': '$time',
                'action': '$data.action',
                'speed': '$data.gpsSpeed',
            }
        }
    ]
    if vehicle_number:
        aggregation_pipeline.append({
            '$match': {
                'vehicleNumber': vehicle_number
            }
        })

    cursor = alarms_payload_collection.aggregate(aggregation_pipeline)
    results = []
    async for document in cursor:
        document['alarmDescription'] = ALARM_TYPE_DESCRIPTIONS.get(
            int(document['alarmCode']), 'Unknown Alarm'
        )
        results.append(document)

    return results


async def handle_alarm_for_gauss(alarm_data: dict):
    """
    Handle alarm data for Gauss. If the alarm is not complete (START and END),
    it will be saved in a cache until the other part is received.
    """
    print('[DEBUG] Inside handle_alarm_for_gauss')
    alarm_id = alarm_data.alarmId
    action = alarm_data.action

    alert_name, alert_type = ALARMS_GAUSS_MAPPING.get(
        alarm_data.alarmType, ("Unknown", "Unknown")
    )

    print(f"[DEBUG] Processing alarm {alert_name} with action {alert_type}")

    if action == "START":
        if alarm_id in alarm_cache and "end" in alarm_cache[alarm_id]:
            print("[WEBHOOK-ALARMS] Found END before "
                  f"START for alarm {alarm_id}. Sending to Gauss.")
            cached_alarm = alarm_cache.pop(alarm_id)
            cached_alarm.update({
                "start": datetime
                        .strptime(alarm_data.startTime, "%Y-%m-%dT%H:%M:%SZ")
                        .strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": float(alarm_data.gpsLat),
                "longitude": float(alarm_data.gpsLng),
                "altitude": float(alarm_data.gpsAltitude or 0),
                "vehicleCode": alarm_data.vehicleNumber.split()[0],
                "alertName": alert_name,
                "type": alert_type,
                "driverCode": alarm_data.driverName,
                "serializedMetaData": {
                    "speed": float(alarm_data.gpsSpeed or 0)
                    },
            })
            await send_alarms_to_gauss([cached_alarm])
        else:
            print(f"[WEBHOOK-ALARMS] Saving START alarm  {alarm_id} in cache.")
            alarm_cache[alarm_id] = {
                "start": datetime
                .strptime(alarm_data.startTime, "%Y-%m-%dT%H:%M:%SZ")
                .strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": float(alarm_data.gpsLat),
                "longitude": float(alarm_data.gpsLng),
                "altitude": float(alarm_data.gpsAltitude or 0),
                "vehicleCode": alarm_data.vehicleNumber.split()[0],
                "alertName": alert_name,
                "type": alert_type,
                "driverCode": alarm_data.driverName,
                "serializedMetaData": {
                    "speed": float(alarm_data.gpsSpeed or 0)
                },
            }

    elif action == "END":
        if alarm_id in alarm_cache and "start" in alarm_cache[alarm_id]:
            print("[WEBHOOK-ALARMS] Found START before "
                  f"END for alarm {alarm_id}. Sending to Gauss.")
            cached_alarm = alarm_cache.pop(alarm_id)
            cached_alarm["end"] = \
                datetime.strptime(
                    alarm_data.endTime, "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%Y-%m-%d %H:%M:%S")
            await send_alarms_to_gauss([cached_alarm])
        else:
            print(f"[WEBHOOK-ALARMS] Saving END alarm {alarm_id} in cache "
                  "for later processing with START.")
            alarm_cache[alarm_id] = {
                "end": datetime
                .strptime(alarm_data.endTime, "%Y-%m-%dT%H:%M:%SZ")
                .strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": float(alarm_data.gpsLat),
                "longitude": float(alarm_data.gpsLng),
                "altitude": float(alarm_data.gpsAltitude or 0),
                "vehicleCode": alarm_data.vehicleNumber.split()[0],
                "alertName": alert_name,
                "type": alert_type,
                "driverCode": alarm_data.driverName,
                "serializedMetaData": {
                    "speed": float(alarm_data.gpsSpeed or 0)
                },
            }
