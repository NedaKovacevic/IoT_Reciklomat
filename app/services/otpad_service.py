from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.db import crud
from app.services.stanje_store import get_stanje

ALLOWED_TYPES = {"plastic", "metal", "cardboard"}


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


def build_status_response(
    db: Session,
    device_id: str,
    device_status: str
) -> dict:
    """
    Pravi kompletan status uredjaja:
    - ON/OFF
    - broj otpada
    - stanje (READY/RUNNING...)
    """

    counts = crud.get_counts_by_device(db, device_id=device_id)

    for k in ["plastic", "metal", "cardboard"]:
        counts.setdefault(k, 0)

    stanje = get_stanje(device_id)
    mode = stanje["mode"] if stanje else None
    last_seen = stanje["last_seen"] if stanje else None

    return {
        "device_id": device_id,
        "status": device_status,
        "counts": counts,
        "mode": mode,
        "last_seen": last_seen,
    }
