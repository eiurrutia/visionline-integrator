from app.utils.database import alarms_collection, alarms_payload_collection
from app.utils.alarm_types import ALARM_TYPE_DESCRIPTIONS
from app.models.alarm_data import AlarmPayload
import os
from datetime import datetime, timezone
from typing import List, Optional

LOG_ALARM_PAYLOAD = os.getenv("LOG_ALARM_PAYLOAD", "false").lower() == 'true'
LOG_ALARM_DATA = os.getenv("LOG_ALARM_DATA", "false").lower() == 'true'


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
        return {
            "status": "success",
            "message": "ALARM data stored successfully"
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
