from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError
from app.models.alarm_data import AlarmPayload
from app.services.alarm_service import process_alarm_data
import os
import json

TENANT_ID = os.getenv("TENANT_ID")

alarm_webhook_router = APIRouter(
    prefix="/webhook/alarms", tags=["Webhook Alarm Data"]
)


@alarm_webhook_router.post("", include_in_schema=False)
@alarm_webhook_router.post("/")
async def receive_alarm_data(request: Request):
    """
    Endpoint to receive alarm data.
    """
    try:
        # Read the raw body of the request
        raw_body = await request.body()
        payload_dict = json.loads(raw_body)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON: {e}"
        )
    try:
        payload = AlarmPayload(**payload_dict)
    except ValidationError as ve:
        print("Validation error:", ve)
        raise HTTPException(
            status_code=422,
            detail=str(ve)
        )

    print(f"[ALARM-WEBHOOK] Received ALARM data. Batch time: {payload.time}. "
          f"Data count: {len(payload.data)}")

    # Check type and tenant ID
    if payload_dict["type"] != "ALARM":
        raise HTTPException(
            status_code=400,
            detail="Invalid payload type. Expected 'ALARM' "
                   f"and received: {payload_dict['type']}."
        )
    if str(payload_dict["tenantId"]) != TENANT_ID:
        raise HTTPException(status_code=403, detail="Invalid tenant ID")

    result = await process_alarm_data(payload)
    if result["status"] == "error":
        print(f"Error processing ALARM data: {result['message']}")
        raise HTTPException(status_code=400, detail=result["message"])

    return {"status": "received", "data": payload.dict()}
