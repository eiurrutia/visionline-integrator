from app.utils.database import gps_collection, gps_payload_collection
from app.models.gps_data import GPSPayload
import os
from datetime import datetime
from typing import List, Optional

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


async def get_gps_data_by_vehicle(
        vehicleNumber: str, 
        start_time: Optional[str] = None,
        limit: int = 100, skip: int = 0) -> List[dict]:
    """
    Get GPS data for a specific vehicle by vehicle number.
    Optionally filter by start time.
    """
    match_filter = {
        'type': 'GPS',
        'data.vehicleNumber': vehicleNumber
    }

    if start_time:
        try:
            match_filter['time'] = {'$gt': start_time}
        except ValueError:
            raise ValueError(
                "`start_time` debe estar en formato ISO 8601, "
                "por ejemplo '2024-12-24T21:00:00Z'"
            )

    aggregation_pipeline = [
        {
            '$match': match_filter
        },
        {
            '$unwind': '$data'
        },
        {
            '$match': {
                'data.vehicleNumber': vehicleNumber
            }
        },
        {
            '$sort': {
                'time': -1
            }
        },
        {
            '$project': {
                '_id': '$_id',
                'docTime': '$time',
                'receivedAt': 1,
                'vehicleNumber': '$data.vehicleNumber',
                'lat': '$data.lat',
                'lng': '$data.lng',
                'speed': '$data.speed',
                'positionTime': '$data.time'
            }
        },
        {
            '$skip': skip
        },
        {
            '$limit': limit
        }
    ]

    cursor = gps_payload_collection.aggregate(aggregation_pipeline)
    results = []
    async for document in cursor:
        results.append(document)

    return results
