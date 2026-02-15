from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WasteEventIn(BaseModel):
    device_id: str
    waste_type: str
    timestamp: Optional[datetime] = None  # moze da se posalje, ali ne mora

class WasteEventOut(BaseModel):
    device_id: str
    waste_type: str
    timestamp: datetime

class StatusOut(BaseModel):
    device_id: str
    status: str
    counts: dict[str, int]
    mode: Optional[str] = None
    last_seen: Optional[datetime] = None

class ControlIn(BaseModel):
    device_id: str



class StanjeIn(BaseModel):
    device_id: str
    mode: str  # BOOTING, READY, RUNNING, ERROR

class StanjeInfo(BaseModel):
    device_id: str
    mode: str
    last_seen: datetime


