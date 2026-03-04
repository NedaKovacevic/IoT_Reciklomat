from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.db.database import get_db
from app.services.stanje_store import upsert_stanje
from app.core.security import require_operator
from app.services.iot_service import start_recognition, stop_recognition

logger = logging.getLogger(__name__)

router = APIRouter(tags=["control"])


@router.post("/start")
def start(
    device_id: str,
    db: Session = Depends(get_db),
    x_role: str = Header(default="viewer"),
    _=Depends(require_operator),
):
    try:
        payload = {"actor_mode": (x_role or "").lower()}
        resp = start_recognition(device_id, payload=payload)
    except Exception as e:
        logger.exception("Start direct method failed")
        raise HTTPException(status_code=502, detail=str(e))

    # BITNO: nemoj upisivati ACTIVE ako uređaj nije prihvatio
    if str(resp.get("status")) != "200":
        return {"status": "rejected", "iot": resp}

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
    x_role: str = Header(default="viewer"),
    _=Depends(require_operator),
):
    try:
        payload = {"actor_mode": (x_role or "").lower()}
        resp = stop_recognition(device_id, payload=payload)
    except Exception as e:
        logger.exception("Stop direct method failed")
        raise HTTPException(status_code=502, detail=str(e))

    if str(resp.get("status")) != "200":
        return {"status": "rejected", "iot": resp}

    upsert_stanje(
        db,
        device_id=device_id,
        recognition_running=False,
        last_seen=datetime.utcnow(),
        mode="IDLE",
    )
    return {"status": "ok", "iot": resp}





