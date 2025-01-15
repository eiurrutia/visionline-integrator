from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import ValidationError
from app.models.alarm_data import AlarmPayload, AlarmRecord
from app.services.alarm_service import process_alarm_data, get_alarms_data
import os
import json
from typing import List, Optional

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
        print("Payload dict:", payload_dict)
        return {
            "status": "received",
            "data": payload.dict(),
            'error': str(ve)
        }

    print(f"[ALARM-WEBHOOK] Received ALARM data. Batch time: {payload.time}. "
          f"Data count: {len(payload.data)}")

    # Check type and tenant ID
    if payload_dict["type"] != "ALARM":
        print("Invalid payload type. Expected 'ALARM' "
              f"and received: {payload_dict['type']}.")
        return {
            "status": "received",
            "data": payload.dict(),
            'error': "Invalid payload type. "
                     f"Expected ALARM and received {payload_dict['type']}"
        }
    if str(payload_dict["tenantId"]) != TENANT_ID:
        raise HTTPException(status_code=403, detail="Invalid tenant ID")

    result = await process_alarm_data(payload)
    if result["status"] == "error":
        print(f"Error processing ALARM data: {result['message']}")
        raise HTTPException(status_code=400, detail=result["message"])

    return {"status": "received", "data": payload.dict()}


alarms_router = APIRouter(prefix="/alarms", tags=["Alarms Data Retrieval"])


@alarms_router.get("/",
                   response_model=List[AlarmRecord],
                   summary="Obtener datos de Alarms. "
                           "Opcional: por número de vehículo")
async def get_gps_records(
    vehicleNumber: Optional[str] = Query(
        None,
        description="Filtro opcional: Número de Vehículo: "
        " (e.g., 'RTBB71')"),
    start_time: Optional[str] = Query(
        None,
        description="Filtro opcional: Tiempo mínimo "
        "en ISO 8601 (e.g., '2024-12-24T21:00:00Z')")
):
    """
    Endpoint to retrieve Alarms data. Optionally by vehicle number.
    """
    print(f"[Alarms] Requesting Alarms. Vehicle: {vehicleNumber}, ")
    try:
        results = await get_alarms_data(
            vehicleNumber, start_time
        )
        return results
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
