from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.models.schemas import StanjeIn, StanjeInfo
from app.db.uredjaj_state_crud import upsert
from app.services.stanje_store import set_stanje, get_all_devices

router = APIRouter(tags=["stanje"])


@router.post("/stanje")
def stanje(payload: StanjeIn, db: Session = Depends(get_db)):
    upsert(
        db,
        device_id=payload.device_id,
        mode=payload.mode,
        last_seen=datetime.utcnow()
    )
    return {"status": "ok"}


@router.get("/devices", response_model=list[StanjeInfo])
def devices():
    return get_all_devices()
