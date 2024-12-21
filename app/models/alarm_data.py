from pydantic import BaseModel
from typing import List


class AlarmData(BaseModel):
    alarmId: str
    vehicleId: str
    alarmType: str
    time: str
    severity: int


class AlarmPayload(BaseModel):
    tenantId: int
    type: str
    time: str
    data: List[AlarmData]
