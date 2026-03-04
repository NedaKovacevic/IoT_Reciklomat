from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Any, Dict
from fastapi.encoders import jsonable_encoder


from app.db import crud
from app.services.stanje_store import get_stanje
from app.services.iot_service import get_device_iothub_status

ALLOWED_TYPES = {"plastic", "glass", "cardboard"}


def handle_waste_event(
    db: Session,
    device_id: str,
    waste_type: str,
    timestamp: Optional[datetime] = None
):
    """
    Upisuje detekciju otpada u bazu.
    """
    if waste_type not in ALLOWED_TYPES:
        raise ValueError(f"Unknown waste type: {waste_type}")

    crud.insert_waste_event(
        db=db,
        device_id=device_id,
        tip_otpada=waste_type,
        vreme_detekcije=timestamp
    )


def build_status_response(db: Session, device_id: str, device_status: Dict[str, Any]) -> dict:
    counts = crud.get_counts_by_device(db, device_id=device_id)
    for k in ["plastic", "glass", "cardboard"]:
        counts.setdefault(k, 0)

    # Tvoje stanje iz baze (mode/last_seen/recognition_running)
    stanje = get_stanje(db, device_id)
    mode = stanje["mode"] if stanje else None
    last_seen = stanje["last_seen"] if stanje else None
    recognition_running = stanje["recognition_running"] if stanje else False


    #povlaci iz IoT Hub-a:
    iothub = get_device_iothub_status(device_id)
    status_str = iothub.get("status") or "unknown"

    return {
        "device_id": device_id,
        "status": status_str,              # enabled/disabled
        "counts": counts,
        "mode": mode,
        "last_seen": last_seen,
        "recognition_running": recognition_running,  # START/STOP program
    }