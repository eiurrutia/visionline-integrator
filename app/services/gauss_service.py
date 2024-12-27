# import httpx
from app.utils.database import gps_gauss_integration_collection
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger("apscheduler")


async def send_gps_data_to_gauss_control(gps_data: list) -> bool:
    payload_id = str(uuid.uuid4())
    logger.info(gps_data)
    try:
        # response = await simulate_migtra_api_call(payload)
        response = {"status": "success",
                    "message": "GPS data sent successfully"}

        await log_gauss_integration(
            payload_id, gps_data, response, "success"
        )
    except Exception as e:
        await log_gauss_integration(
            payload_id, gps_data, None, "failed", str(e)
        )
    return True


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
