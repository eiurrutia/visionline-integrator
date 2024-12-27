from pydantic import BaseModel
from typing import List, Optional, Union


class AlarmData(BaseModel):
    alarmId: str
    alarmType: Optional[int] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    uniqueId: Optional[str] = None
    vehicleId: Optional[str] = None
    gpsAngle: Optional[int] = None
    gpsLat: Optional[str] = None
    gpsLng: Optional[str] = None
    gpsSpeed: Optional[str] = None
    gpsTime: Optional[str] = None
    alarmAdditionalInfo: Optional[dict] = None
    gpsAltitude: Optional[int] = None
    vehicleNumber: Optional[str] = None
    fleetName: Optional[str] = None
    action: Optional[str] = None
    driverName: Optional[str] = None
    jobNumber: Optional[str] = None


class AlarmPayload(BaseModel):
    tenantId: int
    type: str
    time: str
    data: List[AlarmData]


class AlarmRecord(BaseModel):
    _id: str
    alarmCode: Union[str, int]
    time: str
    vehicleNumber: Optional[str] = None
    action: Optional[str] = None
    speed: Optional[str] = None
    alarmDescription: Optional[str] = None

    class Config:
        from_attributes = True
