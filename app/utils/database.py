from motor.motor_asyncio import AsyncIOMotorClient
import os

# Cargar la URI de conexión desde las variables de entorno
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment variables")

# Crear el cliente de MongoDB
client = AsyncIOMotorClient(MONGO_URI)

# Seleccionar la base de datos
db = client["visionaline_db"]

# Crear referencias a las colecciones
gps_collection = db["gps_data"]
alarms_collection = db["alarm_data"]


# Configurar índices si es necesario
async def setup_indexes():
    await gps_collection.create_index("vehicleId")
    await gps_collection.create_index("time")
    await alarms_collection.create_index("vehicleId")
    await alarms_collection.create_index("time")
