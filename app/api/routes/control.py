# app/api/routes/control.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.services.iot_service import start_recognition, stop_recognition
from app.services.stanje_store import upsert_stanje
from app.core.security import require_operator  # ✅ DODAJ

router = APIRouter(tags=["control"])


@router.post("/start", dependencies=[Depends(require_operator)])  # ✅ DODAJ
def start(device_id: str, db: Session = Depends(get_db)):
    try:
        resp = start_recognition(device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    upsert_stanje(
        db,
        device_id=device_id,
        recognition_running=True,
        last_seen=datetime.utcnow(),
        mode="ACTIVE"
    )
    return {"status": "ok", "iot": resp}


@router.post("/stop", dependencies=[Depends(require_operator)])  # ✅ DODAJ
def stop(device_id: str, db: Session = Depends(get_db)):
    try:
        resp = stop_recognition(device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    upsert_stanje(
        db,
        device_id=device_id,
        recognition_running=False,
        last_seen=datetime.utcnow(),
        mode="IDLE"
    )
    return {"status": "ok", "iot": resp}