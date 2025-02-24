from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment variables")

client = AsyncIOMotorClient(MONGO_URI)
db = client["visionaline_db"]

# Create collections
gps_payload_collection = db["gps_payload_data"]
gps_collection = db["gps_data"]
alarms_payload_collection = db["alarms_payload_data"]
alarms_collection = db["alarm_data"]
gps_migtra_integration_collection = db["gps_migtra_integration"]
gps_gauss_integration_collection = db["gps_gauss_integration"]
alarms_gauss_integration_collection = db["alarms_gauss_integration"]


# Setup indexes
async def setup_indexes():
    await gps_payload_collection.create_index(
        "receivedAt",
        expireAfterSeconds=7 * 24 * 3600  # 7 days
    )
    await gps_collection.create_index(
        "receivedAt",
        expireAfterSeconds=7 * 24 * 3600  # 7 days
    )
    await alarms_payload_collection.create_index(
        "receivedAt",
        expireAfterSeconds=7 * 24 * 3600  # 7 days
    )
    await gps_migtra_integration_collection.create_index(
        "sentAt",
        expireAfterSeconds=7 * 24 * 3600  # 7 days
    )
    await gps_gauss_integration_collection.create_index(
        "sentAt",
        expireAfterSeconds=7 * 24 * 3600  # 7 days
    )
    await alarms_gauss_integration_collection.create_index(
        "sentAt",
        expireAfterSeconds=7 * 24 * 3600  # 7 days
    )
