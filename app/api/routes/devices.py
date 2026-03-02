# app/api/routes/devices.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.iot_service import list_devices_basic
from app.services.stanje_store import get_stanje

router = APIRouter(tags=["devices"])


@router.get("/devices")
def devices(db: Session = Depends(get_db)):
    try:
        hub_devices = list_devices_basic(100)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IoT Hub error: {e}")

    out = []

    for d in hub_devices:
        device_id = d.get("device_id")
        if not device_id:
            continue

        stanje = get_stanje(db, device_id)

        out.append(
            {
                "device_id": device_id,
                "status": d.get("status") or "disabled",
                "last_seen": stanje.get("last_seen") if stanje else None,
                "recognition_running": stanje.get("recognition_running", False) if stanje else False,
            }
        )

    return out