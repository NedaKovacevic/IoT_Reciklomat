# app/db/uredjaj_state_crud.py
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.db_models import UredjajState


def get_by_device_id(db: Session, device_id: str) -> Optional[UredjajState]:
    return db.query(UredjajState).filter(UredjajState.device_id == device_id).first()


def get_all(db: Session):
    return db.query(UredjajState).all()


def upsert(
    db: Session,
    device_id: str,
    mode: Optional[str] = None,
    last_seen: Optional[datetime] = None,
    recognition_running: Optional[bool] = None,
    #camera_on: Optional[bool] = None,
) -> UredjajState:
    row = get_by_device_id(db, device_id=device_id)
    if not row:
        row = UredjajState(device_id=device_id)
        db.add(row)

    if mode is not None:
        row.mode = mode
    if last_seen is not None:
        row.last_seen = last_seen
    if recognition_running is not None:
        row.recognition_running = recognition_running
    #if camera_on is not None:
    #    row.camera_on = camera_on

    db.commit()
    db.refresh(row)
    return row