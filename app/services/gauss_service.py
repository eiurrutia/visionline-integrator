import httpx
from app.utils.database import (
    gps_gauss_integration_collection,
    alarms_gauss_integration_collection
)
from datetime import datetime, timezone
import uuid
import logging
import os
from typing import List

logger = logging.getLogger("apscheduler")

GAUSS_TOKEN_URL = os.getenv("GAUSS_TOKEN_URL")
GAUSS_POSITION_UPDATE_URL = os.getenv("GAUSS_POSITION_UPDATE_URL")
GAUSS_USERNAME = os.getenv("GAUSS_USERNAME")
GAUSS_PASSWORD = os.getenv("GAUSS_PASSWORD")
GAUSS_AUTH = os.getenv("GAUSS_AUTH")
GAUSS_INTEGRATION_ACTIVATE = \
    os.getenv("GAUSS_INTEGRATION_ACTIVATE", "false").lower() == "true"

# Token cache
gauss_token = None


def transform_gps_data_for_gauss(gps_data: List[dict]) -> List[dict]:
    """
    Transform GPS data for Gauss API.
    """
    transformed = []
    for data in gps_data:
        transformed.append({
            "latitude": data["lat"],
            "longitude": data["lng"],
            "altitude": data.get("altitude", 0),
            "vehicleCode": data["vehicleNumber"],
            "odometer": data.get("mileage", 0),
            "driverCode": None,
            "start": datetime
            .strptime(data["time"], "%Y-%m-%dT%H:%M:%SZ")
            .strftime("%Y-%m-%d %H:%M:%S"),
            "speed": data["speed"],
            "tags": ""
        })
    return transformed


async def fetch_gauss_token() -> str:
    """
    Fetch a new access token from Gauss API.
    """
    global gauss_token
    try:
        logger.info("[GAUSS API] Fetching token...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GAUSS_TOKEN_URL,
                headers={
                    "Authorization": f"Basic {GAUSS_AUTH}"
                },
                data={
                    "username": GAUSS_USERNAME,
                    "password": GAUSS_PASSWORD,
                    "grant_type": "password"
                },
                timeout=30
            )
            gauss_token = response.json().get("access_token")
            logger.info("[GAUSS API] Token fetched successfully.")
            return gauss_token
    except Exception as e:
        logger.error(f"[GAUSS API] Error fetching token: {e}")
        raise


async def send_gps_data_to_gauss_control(gps_data: list) -> bool:
    """
    Send GPS data to Gauss Control API.
    """
    payload_id = str(uuid.uuid4())
    try:
        transformed_data = transform_gps_data_for_gauss(gps_data)
        if not GAUSS_INTEGRATION_ACTIVATE:
            logger.info("[GAUSS GPS API] Integration is deactivated.")
            await log_gauss_integration(
                gps_gauss_integration_collection,
                payload_id, transformed_data, None, "not_activated"
            )
            return True

        # Ensure token is available
        if not gauss_token:
            await fetch_gauss_token()

        async with httpx.AsyncClient() as client:
            logger.info("[GAUSS GPS API] Sending GPS data.")
            response = await client.post(
                GAUSS_POSITION_UPDATE_URL,
                json=transformed_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {gauss_token}"
                },
                timeout=30
            )
            response.raise_for_status()

            response_data = response.json()
            await log_gauss_integration(
                gps_gauss_integration_collection,
                payload_id, transformed_data, response_data, "success"
            )
            logger.info("[GAUSS GPS API] Data sent successfully "
                        f"for payload ID: {payload_id}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:  # Token expired
            logger.warning("[GAUSS GPS API] Token expired. "
                           "Fetching a new one.")
            await fetch_gauss_token()
            return await send_gps_data_to_gauss_control(gps_data)
        await log_gauss_integration(
            gps_gauss_integration_collection,
            payload_id, gps_data, None, "failed", str(e)
        )
        logger.error(f"[GAUSS GPS API] HTTP error: {e}")
    except Exception as e:
        await log_gauss_integration(
            gps_gauss_integration_collection,
            payload_id, gps_data, None, "failed", str(e)
        )
        logger.error(f"[GAUSS GPS API] Exception while sending data: {e}")
    return True


async def send_alarms_to_gauss(alarms: List[dict]):
    """
    Send alarms to Gauss Control API.
    """
    payload_id = str(uuid.uuid4())
    try:
        if not GAUSS_INTEGRATION_ACTIVATE:
            logger.info("[GAUSS ALARMS API] Integration is deactivated.")
            await log_gauss_integration(
                alarms_gauss_integration_collection,
                payload_id, alarms, None, "not_activated"
            )
            return True
        if not gauss_token:
            await fetch_gauss_token()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                GAUSS_POSITION_UPDATE_URL,
                json=alarms,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {gauss_token}"
                },
                timeout=30
            )
            response.raise_for_status()
            logger.info("[GAUSS API] Alarms sent successfully: "
                        f"{response.json()}")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:  # Token expired
            logger.warning("[GAUSS API] Token expired. Fetching a new one.")
            await fetch_gauss_token()
            return await send_alarms_to_gauss(alarms)
        logger.error(f"[GAUSS API] HTTP error: {e}")
    except Exception as e:
        logger.error(f"[GAUSS API] Exception while sending alarms: {e}")


async def log_gauss_integration(
        collection,
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
        await collection.insert_one(record)
        logger.info("[GAUSS INTEGRATION] Log saved for payload ID: "
                    f"{payload_id} in collection: {collection.name}")
    except Exception as e:
        logger.info("[GAUSS INTEGRATION] Error saving log for payload ID: "
                    f"{payload_id} - {e} in collection: {collection.name}")
