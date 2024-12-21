from fastapi import APIRouter
from app.models.gps_data import GPSPayload

router = APIRouter(prefix="/gps", tags=["GPS Data"])


@router.post("/", include_in_schema=True)
async def receive_gps_data(payload: GPSPayload):
    print("Received GPS data")
    print(payload.dict())
    return {"status": "received", "data": payload}
