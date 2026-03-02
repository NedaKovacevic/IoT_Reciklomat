# app/db/uredjaj_state_crud.py

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.uredjaj_state import UredjajState


def upsert_state(db: Session, device_id: str, mode: str) -> UredjajState:
    now = datetime.utcnow()
    row = db.query(UredjajState).filter(UredjajState.device_id == device_id).first()

    if row is None:
        row = UredjajState(device_id=device_id, mode=mode, last_seen=now)
        db.add(row)
    else:
        row.mode = mode
        row.last_seen = now

    db.commit()
    db.refresh(row)
    return row


def get_state(db: Session, device_id: str) -> Optional[UredjajState]:
    return db.query(UredjajState).filter(UredjajState.device_id == device_id).first()


def list_states(db: Session) -> List[UredjajState]:
    return db.query(UredjajState).all()