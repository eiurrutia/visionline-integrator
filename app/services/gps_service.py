from app.utils.database import gps_collection
from app.models.gps_data import GPSPayload


async def process_gps_data(payload: GPSPayload):
    try:
        if payload.type != "GPS":
            return {"status": "error", "message": "Invalid payload type"}

        for gps_data in payload.data:
            document = gps_data.dict()
            await gps_collection.insert_one(document)
            print(f"Saved GPS data for vehicle {gps_data.vehicleId}")

        return {"status": "success", "message": "GPS data stored successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
