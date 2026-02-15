from fastapi import APIRouter
from app.models.schemas import StanjeIn, StanjeInfo
from app.services.stanje_store import set_stanje, get_all_devices

router = APIRouter(tags=["stanje"])

@router.post("/stanje")
def stanje(hb: StanjeIn):
    set_stanje(hb.device_id, hb.mode)
    return {"status": "ok"}

@router.get("/devices", response_model=list[StanjeInfo])
def devices():
    return get_all_devices()
