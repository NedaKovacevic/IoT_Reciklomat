# app/api/routes/control.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.db.database import get_db
from app.services.stanje_store import upsert_stanje
from app.core.security import require_operator
from app.services.iot_service import start_recognition, stop_recognition, camera_on, camera_off

logger = logging.getLogger(__name__)

router = APIRouter(tags=["control"])


@router.post("/start")
def start(
    device_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_operator),   # 👈 OVAKO da bi Swagger prikazao x-role
):
    try:
        resp = start_recognition(device_id)
    except Exception as e:
        logger.exception("Start direct method failed")
        raise HTTPException(status_code=502, detail=str(e))

    upsert_stanje(
        db,
        device_id=device_id,
        recognition_running=True,
        last_seen=datetime.utcnow(),
        mode="ACTIVE",
    )

    return {"status": "ok", "iot": resp}


@router.post("/stop")
def stop(
    device_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_operator),   # 👈 isto i ovde
):
    try:
        resp = stop_recognition(device_id)
    except Exception as e:
        logger.exception("Stop direct method failed")
        raise HTTPException(status_code=502, detail=str(e))

    upsert_stanje(
        db,
        device_id=device_id,
        recognition_running=False,
        last_seen=datetime.utcnow(),
        mode="IDLE",
    )

    return {"status": "ok", "iot": resp}



from app.services.iot_service import camera_on, camera_off


@router.post("/camera/on")
def turn_camera_on(
    device_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_operator),
):
    try:
        resp = camera_on(device_id)
    except Exception as e:
        logger.exception("Camera ON direct method failed")
        raise HTTPException(status_code=502, detail=str(e))

    upsert_stanje(
        db,
        device_id=device_id,
        camera_on=True,
        last_seen=datetime.utcnow(),
        mode="CAMERA_ON",
    )

    return {"status": "ok", "iot": resp}


@router.post("/camera/off")
def turn_camera_off(
    device_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_operator),
):
    try:
        resp = camera_off(device_id)
    except Exception as e:
        logger.exception("Camera OFF direct method failed")
        raise HTTPException(status_code=502, detail=str(e))

    upsert_stanje(
        db,
        device_id=device_id,
        camera_on=False,
        last_seen=datetime.utcnow(),
        mode="CAMERA_OFF",
    )

    return {"status": "ok", "iot": resp}