# app/api/routes/control.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.iot_service import start_recognition, stop_recognition
from app.services.stanje_store import upsert_stanje

router = APIRouter(tags=["control"])


@router.post("/start")
def start(device_id: str, db: Session = Depends(get_db)):
    try:
        resp = start_recognition(device_id)
    except Exception as e:
        # Not Found iz IoT Hub-a => uređaj nema tu metodu ili je pogrešno ime
        raise HTTPException(status_code=502, detail=str(e))

    # ako IoT hub call prođe, mi beležimo da je recognition upaljen
    upsert_stanje(db, device_id=device_id, recognition_running=True)
    return {"status": "ok", "iot": resp}


@router.post("/stop")
def stop(device_id: str, db: Session = Depends(get_db)):
    try:
        resp = stop_recognition(device_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    upsert_stanje(db, device_id=device_id, recognition_running=False)
    return {"status": "ok", "iot": resp}