from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import ValidationError
from app.models.gps_data import GPSPayload, GPSRecord
from app.services.gps_service import process_gps_data, get_gps_data_by_vehicle
import os
import json
from typing import List, Optional

TENANT_ID = os.getenv("TENANT_ID")

gps_webhook_router = APIRouter(
    prefix="/webhook/gps", tags=["Webhook GPS Data"]
)


@gps_webhook_router.post("", include_in_schema=False)
@gps_webhook_router.post("/")
async def receive_gps_data(request: Request):
    """
    Endpoint to receive GPS data from Visionaline devices.
    """
    try:
        raw_body = await request.body()
        payload_dict = json.loads(raw_body)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        print(f"Raw body: {raw_body}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON: {e}"
        )
    try:
        payload = GPSPayload(**payload_dict)
    except ValidationError as ve:
        print("Validation error:", ve)
        print("Payload dict:", payload_dict)
        return {
            "status": "received",
            "data": payload_dict,
            'error': str(ve)
        }

    print(f"[GPS-WEBHOOK] Received GPS data. Batch time: {payload.time}. "
          f"Data count: {len(payload.data)}")

    # Check type and tenant ID
    if payload.type != "GPS":
        print(f"Invalid payload type. Expected 'GPS' "
              f"and received '{payload.type}'")
        return {
            "status": "received",
            "data": payload_dict,
            'error': "Invalid payload type. "
                     f"Expected GPS and received {payload.type}"
        }
    if str(payload.tenantId) != TENANT_ID:
        raise HTTPException(status_code=403, detail="Invalid tenant ID")

    result = await process_gps_data(payload)
    if result["status"] == "error":
        print(f"Error processing GPS data: {result['message']}")
        raise HTTPException(status_code=400, detail=result["message"])

    return {"status": "received", "data": payload.dict()}


gps_router = APIRouter(prefix="/gps", tags=["GPS Data Retrieval"])


@gps_router.get("/{vehicleNumber}",
                response_model=List[GPSRecord],
                summary="Obtener datos GPS por número de vehículo")
async def get_gps_records(
    vehicleNumber: str,
    start_time: Optional[str] = Query(
        None,
        description="Filtro opcional: Tiempo mínimo "
        "en ISO 8601 (e.g., '2024-12-24T21:00:00Z')"),
    limit: int = Query(
        100, ge=1, le=1000,
        description="Número máximo de registros a retornar"),
    skip: int = Query(
        0, ge=0,
        description="Número de registros a omitir")
):
    """
    Endpoint to retrieve GPS data by vehicle number.
    """
    print(f"[GPS] Requesting GPS data for vehicle {vehicleNumber}")
    try:
        results = await get_gps_data_by_vehicle(
            vehicleNumber, start_time, limit, skip
        )
        return results
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
