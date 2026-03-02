# app/api/routes/devices.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.iot_service import list_devices_basic
from app.services.stanje_store import get_stanje

router = APIRouter(tags=["devices"])


@router.get("/devices")
def devices(db: Session = Depends(get_db)):
    # IoT Hub spisak (enabled/disabled + connection_state + last_activity_time)
    hub_devices = list_devices_basic(100)

    out = []
    for d in hub_devices:
        device_id = d.get("device_id")
        stanje = get_stanje(db, device_id) if device_id else None

        out.append(
            {
                "device_id": device_id,
                "status": d.get("status"),  # enabled/disabled
                "connection_state": d.get("connection_state"),
                "hub_last_activity_time": d.get("last_activity_time"),
                #"mode": stanje["mode"] if stanje else None,
                #"last_seen": stanje["last_seen"] if stanje else None,
                "recognition_running": stanje["recognition_running"] if stanje else False,
            }
        )

    return out
#komentar