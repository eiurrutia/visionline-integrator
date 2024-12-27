from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class GPSData(BaseModel):
    id: str
    uniqueId: str
    vehicleId: str

    angle: Optional[int] = None

    lat: Optional[float] = None
    lng: Optional[float] = None

    speed: Optional[float] = None
    time: Optional[str] = None

    numOfSatellites: Optional[int] = None
    hdop: Optional[float] = None
    signalStrength: Optional[int] = None
    acc: Optional[int] = None
    altitude: Optional[int] = None
    vehicleNumber: Optional[str] = None
    fleetName: Optional[str] = None

    mileage: Optional[float] = None

    extendData: Optional[str] = None
    sentToMigtra: Optional[bool] = False
    sentToGaussControl: Optional[bool] = False


class GPSPayload(BaseModel):
    tenantId: int
    type: str
    time: str
    data: List[GPSData]


class GPSRecord(BaseModel):
    _id: str
    docTime: str
    receivedAt: str
    vehicleNumber: str
    lat: float
    lng: float
    speed: float
    positionTime: str

    class Config:
        from_attributes = True


class GPSIntegrationRecord(BaseModel):
    payloadId: str
    sentAt: datetime
    payload: dict
    response: Any
    status: str
    errorMessage: Optional[str] = None
