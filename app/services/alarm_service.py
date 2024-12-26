from app.utils.database import alarms_collection, alarms_payload_collection
from app.models.alarm_data import AlarmPayload
import os
from datetime import datetime

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
                "receivedAt": datetime.utcnow().isoformat(),
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
