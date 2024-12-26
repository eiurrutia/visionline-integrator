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


# Setup indexes
async def setup_indexes():
    await gps_payload_collection.create_index("time")
    await gps_collection.create_index("vehicleId")
    await gps_collection.create_index("time")
    await alarms_payload_collection.create_index("time")
    await alarms_collection.create_index("vehicleId")
    await alarms_collection.create_index("time")
