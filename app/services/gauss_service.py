# import httpx
from app.utils.database import gps_gauss_integration_collection
from datetime import datetime, timezone
import uuid
import logging
from typing import List

logger = logging.getLogger("apscheduler")


async def send_gps_data_to_gauss_control(gps_data: list) -> bool:
    payload_id = str(uuid.uuid4())
    try:
        transformed_data = \
            transform_gps_data_for_gauss(gps_data)
        # response = await simulate_migtra_api_call(payload)
        response = {"status": "success",
                    "message": "GPS data sent successfully"}

        await log_gauss_integration(
            payload_id, transformed_data, response, "success"
        )
    except Exception as e:
        await log_gauss_integration(
            payload_id, transformed_data, None, "failed", str(e)
        )
    return True


def transform_gps_data_for_gauss(
        gps_data: List[dict]) -> List[dict]:
    """
    Transform GPS data for Migtra API.
    """
    transformed = []
    for data in gps_data:
        transformed.append({
            "vehicleCode": data["vehicleNumber"],
            "driverCode": None,
            "start":
                datetime
                .strptime(data["time"], "%Y-%m-%dT%H:%M:%SZ")
                .strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": data["lat"],
            "longitude": data["lng"],
            "altitude": data.get("altitude", 0),
            "speed": data["speed"],
            "tags": "",
        })
    return transformed


async def log_gauss_integration(
        payload_id: str, payload: dict,
        response: dict, status: str,
        error_message: str = None):
    """
    Save log for Gauss Integration.
    """
    try:
        record = {
            "payloadId": payload_id,
            "sentAt": datetime.now(timezone.utc),
            "payload": payload,
            "response": response,
            "status": status,
            "errorMessage": error_message,
        }
        await gps_gauss_integration_collection.insert_one(record)
        logger.info("[GAUSS INTEGRATION] Log saved for "
                    F"payload ID: {payload_id}")
    except Exception as e:
        logger.info("[GAUSS INTEGRATION] Error saving log for "
                    f"payload ID: {payload_id} - {e}")
