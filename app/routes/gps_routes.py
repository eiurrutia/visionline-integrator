from fastapi import APIRouter, HTTPException, Request
from app.models.gps_data import GPSPayload
from app.services.gps_service import process_gps_data
import os
import json
from pydantic import ValidationError

TENANT_ID = os.getenv("TENANT_ID")

router = APIRouter(prefix="/webhook/gps", tags=["Webhook GPS Data"])


@router.post("", include_in_schema=False)
@router.post("/")
async def receive_gps_data(request: Request):
    """
    Endpoint to receive GPS data from Visionaline devices.
    """
    try:
        raw_body = await request.body()
        payload_dict = json.loads(raw_body)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON: {e}"
        )
    try:
        payload = GPSPayload(**payload_dict)
    except ValidationError as ve:
        print("Validation error:", ve)
        raise HTTPException(
            status_code=422,
            detail=str(ve)
        )

    print("Received GPS data. Batch time:", payload.time)
    print("Data count:", len(payload.data))

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

    return {"status": "received", "data": payload.dict()}
