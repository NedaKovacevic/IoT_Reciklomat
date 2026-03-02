from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional


class StatusOut(BaseModel):
    """Status koji UI koristi na /status."""

    device_id: str

    # IoT Hub status (enabled/disabled/unknown)
    status: str

    # Brojači detekcija
    counts: Dict[str, int]

    # Backend stanje iz baze
    mode: Optional[str] = None

    # ISO string (dolazi iz stanje_store)
    last_seen: Optional[str] = None

    # Kontrole
    recognition_running: bool = False
    #camera_on: bool = False


class WasteEventIn(BaseModel):
    device_id: str
    waste_type: str
    timestamp: Optional[datetime] = None


class WasteEventOut(BaseModel):
    device_id: str
    waste_type: str
    timestamp: datetime


class ControlIn(BaseModel):
    device_id: str


class StanjeIn(BaseModel):
    device_id: str
    mode: str  # BOOTING, READY, RUNNING, ERROR


class StanjeInfo(BaseModel):
    device_id: str
    mode: str
    last_seen: datetime