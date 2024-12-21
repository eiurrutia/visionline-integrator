from pydantic import BaseModel
from typing import List, Optional


class GPSData(BaseModel):
    id: str
    uniqueId: str
    vehicleId: str
    angle: int
    lat: float
    lng: float
    speed: float
    time: str
    numOfSatellites: int
    hdop: float
    signalStrength: int
    acc: int
    altitude: int
    vehicleNumber: str
    fleetName: str
    mileage: float
    extendData: Optional[str]


class GPSPayload(BaseModel):
    tenantId: int
    type: str
    time: str
    data: List[GPSData]
