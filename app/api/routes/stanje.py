from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.models.schemas import StanjeIn, StanjeInfo
from app.db.uredjaj_state_crud import upsert
from app.services.stanje_store import set_stanje, get_all_devices

#router = APIRouter(tags=["stanje"])
router = APIRouter()

@router.post("/stanje")
def stanje(payload: StanjeIn, db: Session = Depends(get_db)):
    upsert(
        db,
        device_id=payload.device_id,
        mode=payload.mode,
        last_seen=datetime.utcnow()
    )
    return {"status": "ok"}


#@router.get("/stanje/devices")
#def devices(db: Session = Depends(get_db)):
    #return get_all_devices(db)
