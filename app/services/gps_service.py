from app.utils.database import gps_collection, gps_payload_collection
from app.models.gps_data import GPSPayload
import os
from datetime import datetime


LOG_GPS_PAYLOAD = os.getenv("LOG_GPS_PAYLOAD", "false").lower() == 'true'
LOG_GPS_DATA = os.getenv("LOG_GPS_DATA", "false").lower() == 'true'


async def process_gps_data(payload: GPSPayload):
    try:
        if LOG_GPS_DATA:
            for gps_data in payload.data:
                document = gps_data.dict()
                await gps_collection.insert_one(document)
                print(f"Saved GPS data for vehicle {gps_data.vehicleId}")

        if LOG_GPS_PAYLOAD:
            payload_doc = {
                "tenantId": payload.tenantId,
                "type": payload.type,
                "time": payload.time,
                "receivedAt": datetime.utcnow().isoformat(),
                "dataCount": len(payload.data),
                "data": [gps_data.dict() for gps_data in payload.data]
            }
            await gps_payload_collection.insert_one(payload_doc)
            print("Saved entire GPS payload document.")

        return {"status": "success", "message": "GPS data stored successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
