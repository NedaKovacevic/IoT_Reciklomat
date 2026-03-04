from typing import Any, Dict, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.db import uredjaj_state_crud


def _row_to_dict(row) -> Dict[str, Any]:
    return {
        "device_id": row.device_id,
        "mode": row.mode,
        "last_seen": row.last_seen.isoformat() if row.last_seen else None,
        "recognition_running": bool(row.recognition_running) if row.recognition_running is not None else False,
        #"camera_on": bool(row.camera_on) if row.camera_on is not None else False,
    }


def get_stanje(db: Session, device_id: str) -> Optional[Dict[str, Any]]:
    row = uredjaj_state_crud.get_by_device_id(db, device_id=device_id)
    if not row:
        return None
    return _row_to_dict(row)


def upsert_stanje(
    db: Session,
    device_id: str,
    mode: Optional[str] = None,
    last_seen: Optional[datetime] = None,
    recognition_running: Optional[bool] = None,
    #camera_on: Optional[bool] = None,
) -> Dict[str, Any]:
    row = uredjaj_state_crud.upsert(
        db,
        device_id=device_id,
        mode=mode,
        last_seen=last_seen,
        recognition_running=recognition_running,
        #camera_on=camera_on
    )
    return _row_to_dict(row)


def set_stanje(db: Session, device_id: str, mode: str) -> Dict[str, Any]:
    return upsert_stanje(
        db,
        device_id=device_id,
        mode=mode,
        last_seen=datetime.utcnow(),
    )


def get_all_devices(db: Session):
    return uredjaj_state_crud.get_all(db)