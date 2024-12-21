from app.models.alarm_data import AlarmPayload


async def process_alarm_data(payload: AlarmPayload):
    if payload.type != "ALARM":
        return {"status": "error", "message": "Invalid payload type"}

    for alarm_data in payload.data:
        print(f"Processing Alarm {alarm_data.alarmId} "
              f"for vehicle {alarm_data.vehicleId}")
        # Data processing logic goes here and API calls can be made
    return {
        "status": "success",
        "message": "Alarm data processed successfully"
    }
