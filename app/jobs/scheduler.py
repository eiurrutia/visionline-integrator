from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.migtra_service import send_gps_data_to_migtra
from app.services.gauss_service import send_gps_data_to_gauss_control
from app.utils.database import gps_collection
import logging

logger = logging.getLogger("apscheduler")


async def process_and_send_migtra():
    """Process and send data to Migtra."""
    gps_records = await gps_collection.find({
        "sentToMigtra": False
    }).to_list(None)
    logger.info("[MIGTRA] Task scheduled to send GPS data to Migtra. "
                f"Total payloads: {len(gps_records)}")

    gps_data = []
    for record in gps_records:
        gps_data.append({
            "id": record["id"],
            "asset": record["uniqueId"],
            "dtgps": record["time"],
            "dtrx": record["receivedAt"],
            "lat": record["lat"],
            "lon": record["lng"],
            "alt": record.get("altitude", 0),
            "spd": record["speed"],
            "angle": record["angle"],
            "dop": record.get("hdop", 0),
            "fix": record.get("numOfSatellites", 0),
            "ign": record["acc"],
            "vehicleNumber": record["vehicleNumber"],
            "fleetName": record["fleetName"],
            "receivedAt": record["receivedAt"],
            "time": record["time"]
        })

    if gps_data:
        success = await send_gps_data_to_migtra(gps_data)
        if success:
            gps_ids = [record["_id"] for record in gps_records]
            await gps_collection.update_many(
                {"_id": {"$in": gps_ids}},
                {"$set": {"sentToMigtra": True}}
            )
            logger.info("[MIGTRA] GPS data sent to Migtra. Records updated.")


async def process_and_send_gauss_control():
    """Process and send data to Gauss Control."""
    gps_records = await gps_collection.find({
        "sentToGaussControl": False
    }).to_list(None)
    logger.info("[GAUSS] Task scheduled to send GPS data to Migtra. "
                f"Total payloads: {len(gps_records)}")

    gps_data = []
    for record in gps_records:
        gps_data.append({
            "id": record["id"],
            "asset": record["uniqueId"],
            "dtgps": record["time"],
            "dtrx": record["receivedAt"],
            "lat": record["lat"],
            "lon": record["lng"],
            "alt": record.get("altitude", 0),
            "spd": record["speed"],
            "angle": record["angle"],
            "dop": record.get("hdop", 0),
            "fix": record.get("numOfSatellites", 0),
            "ign": record["acc"],
            "vehicleNumber": record["vehicleNumber"],
            "fleetName": record["fleetName"],
            "receivedAt": record["receivedAt"],
            "time": record["time"]
        })

    if gps_data:
        success = await send_gps_data_to_gauss_control(gps_data)
        if success:
            gps_ids = [record["_id"] for record in gps_records]
            await gps_collection.update_many(
                {"_id": {"$in": gps_ids}},
                {"$set": {"sentToGaussControl": True}}
            )
            logger.info("[GAUSS] GPS data sent to "
                        "Gauss Control. Records updated.")

# Settup del scheduler
scheduler = AsyncIOScheduler()

# Schedule jobs
scheduler.add_job(process_and_send_migtra, CronTrigger(second="0,30"))
scheduler.add_job(process_and_send_gauss_control, CronTrigger(second="10,40"))


def start_scheduler():
    scheduler.start()
