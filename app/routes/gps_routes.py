from fastapi import APIRouter, HTTPException
from app.models.gps_data import GPSPayload
from app.services.gps_service import process_gps_data
import os

TENANT_ID = os.getenv("TENANT_ID")

router = APIRouter(prefix="/webhook/gps", tags=["Webhook GPS Data"])


@router.post("", include_in_schema=False)
@router.post("/")
async def receive_gps_data(payload: GPSPayload):
    print("Received GPS data")
    print(payload.dict())

    # Check type and tenant ID
    if payload.type != "GPS":
        raise HTTPException(
            status_code=400,
            detail="Invalid payload type. Expected 'GPS' "
                   f"and received '{payload.type}'"
            )
    if str(payload.tenantId) != TENANT_ID:
        raise HTTPException(status_code=403, detail="Invalid tenant ID")

    result = await process_gps_data(payload)
    if result["status"] == "error":
        print(f"Error processing GPS data: {result['message']}")
        raise HTTPException(status_code=400, detail=result["message"])

    return {"status": "received", "data": payload}
