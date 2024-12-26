from fastapi import FastAPI
from app.routes.gps_routes import webhook_router, gps_router
from app.utils.database import setup_indexes

app = FastAPI(title="Visionline API Integration")

# Register the routers
app.include_router(webhook_router)
app.include_router(gps_router)


@app.on_event("startup")
async def startup_event():
    await setup_indexes()


@app.get("/")
async def root():
    return {"message": "Welcome to Visionline API-Middleware"}
