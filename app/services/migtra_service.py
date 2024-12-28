import httpx
from app.utils.database import gps_migtra_integration_collection
from datetime import datetime, timezone
import uuid
import logging
import os
from typing import List

logger = logging.getLogger("apscheduler")

MIGTRA_URL = os.getenv("MIGTRA_URL")
MIGTRA_USERNAME = os.getenv("MIGTRA_USERNAME")
MIGTRA_PASSWORD = os.getenv("MIGTRA_PASSWORD")
MIGTRA_INTEGRATION_ACTIVATE = \
    os.getenv("MIGTRA_INTEGRATION_ACTIVATE", "false").lower() == 'true'


async def send_gps_data_to_migtra(gps_data: List[dict]) -> bool:
    payload_id = str(uuid.uuid4())
    try:
        transformed_data = \
            transform_gps_data_for_migtra(payload_id, gps_data)

        if MIGTRA_INTEGRATION_ACTIVATE:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    MIGTRA_URL,
                    json=transformed_data,
                    headers={"Content-Type": "application/json"},
                    auth=(MIGTRA_USERNAME, MIGTRA_PASSWORD),
                    timeout=30
                )
                logger.info(f"[MIGTRA API] Response: {response.json()}")

            response_data = response.json()
            if response.status_code == 200:
                await log_migtra_integration(
                    payload_id, gps_data, response_data, "success"
                )
                logger.info("[MIGTRA API] Data sent successfully "
                            f"for payload ID: {payload_id}")
            else:
                await log_migtra_integration(
                    payload_id, gps_data, response_data, "failed"
                )
                logger.error("[MIGTRA API] Failed to send data. "
                             f"Payload ID: {payload_id}, "
                             f"Response: {response_data}")
                return False
        else:
            logger.info("[MIGTRA API] Integration is not activated. "
                        "Data not sent.")
            await log_migtra_integration(
                payload_id, gps_data, None, "not_activated"
            )
            return True

    except Exception as e:
        await log_migtra_integration(
            payload_id, gps_data, None, "failed", str(e)
        )
        logger.error(f"[MIGTRA API] Exception while sending data: {e}")
        return False
    return True


def transform_gps_data_for_migtra(
        payload_id: str,
        gps_data: List[dict]) -> List[dict]:
    """
    Transform GPS data for Migtra API.
    """
    transformed = []
    for data in gps_data:
        transformed.append({
            "id": payload_id,
            "asset": data["vehicleNumber"],
            "dtgps": data["time"],
            "dtrx": data["receivedAt"].isoformat()
            if isinstance(data["receivedAt"], datetime)
            else data["receivedAt"],
            "lat": data["lat"],
            "lon": data["lng"],
            "alt": data.get("altitude", 0),
            "spd": data["speed"],
            "angle": data["angle"],
            "dop": data.get("hdop", 0),
            "ign": data.get("acc", 0)
        })
    return transformed


async def log_migtra_integration(
        payload_id: str, payload: dict,
        response: dict, status: str,
        error_message: str = None):
    """
    Save log for Migtra Integration.
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
        await gps_migtra_integration_collection.insert_one(record)
        logger.info("[MIGTRA INTEGRATION] Log saved for "
                    f"payload ID: {payload_id}")
    except Exception as e:
        logger.info("[MIGTRA INTEGRATION] Error saving log for "
                    f"payload ID: {payload_id} - {e}")
