from fastapi import APIRouter
from app.models.alarm_data import AlarmPayload
from app.services.alarm_service import process_alarm_data

router = APIRouter()


@router.post("/")
async def receive_alarm_data(payload: AlarmPayload):
    return await process_alarm_data(payload)
