# app/services/stanje_store.py
from typing import Any, Dict, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.db import uredjaj_state_crud


def get_stanje(db: Session, device_id: str) -> Optional[Dict[str, Any]]:
    row = uredjaj_state_crud.get_by_device_id(db, device_id=device_id)
    if not row:
        return None
    return {
        "device_id": row.device_id,
        "mode": row.mode,
        "last_seen": row.last_seen.isoformat() if row.last_seen else None,
        "recognition_running": bool(row.recognition_running) if row.recognition_running is not None else False,
    }


def upsert_stanje(
    db: Session,
    device_id: str,
    mode: Optional[str] = None,
    last_seen: Optional[datetime] = None,
    recognition_running: Optional[bool] = None,
) -> Dict[str, Any]:
    row = uredjaj_state_crud.upsert(
        db,
        device_id=device_id,
        mode=mode,
        last_seen=last_seen,
        recognition_running=recognition_running,
    )
    return {
        "device_id": row.device_id,
        "mode": row.mode,
        "last_seen": row.last_seen.isoformat() if row.last_seen else None,
        "recognition_running": bool(row.recognition_running) if row.recognition_running is not None else False,
    }