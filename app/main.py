from fastapi import FastAPI
import os
import app.utils.logging_config as logging_config  # noqa: F401
from app.routes.gps_routes import gps_webhook_router, gps_router
from app.routes.alarm_routes import alarm_webhook_router, alarms_router
from app.utils.database import setup_indexes
from app.jobs.scheduler import start_scheduler

SCHEDULER_TO_SEND_GPS_ACTIVATE = \
    os.getenv("SCHEDULER_TO_SEND_GPS_ACTIVATE", "false").lower() == 'true'

app = FastAPI(title="Visionline API Integration")

# Register the routers
app.include_router(gps_webhook_router)
app.include_router(gps_router)

app.include_router(alarm_webhook_router)
app.include_router(alarms_router)


@app.on_event("startup")
async def startup_event():
    await setup_indexes()
    if SCHEDULER_TO_SEND_GPS_ACTIVATE:
        start_scheduler()


@app.get("/")
async def root():
    return {"message": "Welcome to Visionline API-Middleware"}
