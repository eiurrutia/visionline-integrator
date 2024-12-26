from fastapi import APIRouter, HTTPException, Request
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

    print("[ALARM-WEBHOOK] Raw payload received:\n",
          json.dumps(payload_dict, indent=4))

    # Check type and tenant ID
    if payload_dict["type"] != "ALARM":
        raise HTTPException(
            status_code=400,
            detail="Invalid payload type. Expected 'ALARM' "
                   f"and received: {payload_dict['type']}."
        )
    if str(payload_dict["tenantId"]) != TENANT_ID:
        raise HTTPException(status_code=403, detail="Invalid tenant ID")

    return {
        "status": "received",
        "message": "Payload received and printed successfully"
    }
