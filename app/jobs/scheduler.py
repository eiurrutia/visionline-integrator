from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.migtra_service import send_gps_data_to_migtra
from app.services.gauss_service import send_gps_data_to_gauss_control
from app.utils.database import gps_collection
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger("apscheduler")


async def process_and_send_migtra():
    """Process and send data to Migtra."""
    gps_data = await gps_collection.find({
        "sentToMigtra": False
    }).to_list(None)
    logger.info("[MIGTRA] Task scheduled to send GPS data to Migtra. "
                f"Total payloads: {len(gps_data)}")

    if gps_data:
        success = await send_gps_data_to_migtra(gps_data)
        if success:
            gps_ids = [record["_id"] for record in gps_data]
            await gps_collection.update_many(
                {"_id": {"$in": gps_ids}},
                {"$set": {"sentToMigtra": True}}
            )
            logger.info("[MIGTRA] GPS data sent to Migtra. Records updated.")


async def process_and_send_gauss_control():
    """
    Process and send data to Gauss Control.
    Sends only the last GPS position per vehicle in the last minute.
    """
    # Define the time range for filtering
    one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=3)

    # Fetch GPS data within the last minute
    gps_data = await gps_collection.find({
        "sentToGaussControl": False,
        "time": {"$gte": one_minute_ago.isoformat() + "Z"}
    }).to_list(None)

    logger.info("[GAUSS] Task scheduled to send GPS data to Gauss. "
                f"Total raw payloads: {len(gps_data)}")

    if not gps_data:
        logger.info("[GAUSS] No GPS data to process.")
        return

    # Filter to get only the latest position per vehicle
    latest_positions = {}
    for record in gps_data:
        vehicle_number = record["vehicleNumber"]
        record_time = datetime.strptime(record["time"], "%Y-%m-%dT%H:%M:%SZ")
        if (vehicle_number not in latest_positions or
            record_time > datetime.strptime(
                latest_positions[vehicle_number]["time"],
                "%Y-%m-%dT%H:%M:%SZ"
                )):
            latest_positions[vehicle_number] = record

    # Prepare the filtered data
    filtered_data = list(latest_positions.values())
    logger.info("[GAUSS] Filtered GPS data to send. "
                f"Unique vehicles: {len(filtered_data)}")

    # Send the filtered data to Gauss
    success = await send_gps_data_to_gauss_control(filtered_data)
    if success:
        gps_ids = [record["_id"] for record in gps_data]
        await gps_collection.update_many(
            {"_id": {"$in": gps_ids}},
            {"$set": {"sentToGaussControl": True}}
        )
        logger.info("[GAUSS] GPS data sent to Gauss Control. Records updated.")

# Settup del scheduler
scheduler = AsyncIOScheduler()

# Schedule jobs
scheduler.add_job(process_and_send_migtra, CronTrigger(second="0,30"))
scheduler.add_job(process_and_send_gauss_control, CronTrigger(second="10"))


def start_scheduler():
    scheduler.start()
