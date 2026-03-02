from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.database import get_db
from app.core.config import DEVICE_ID_DEFAULT
from app.models.schemas import StatusOut
from app.services.iot_service import get_device_iothub_status
from app.services.otpad_service import build_status_response
from app.services.stanje_store import get_stanje

router = APIRouter(tags=["status"])


@router.get("/status", response_model=StatusOut)
def status(device_id: str = DEVICE_ID_DEFAULT, db: Session = Depends(get_db)):
    try:
        device_status = get_device_iothub_status(device_id)

        base = build_status_response(
            db=db,
            device_id=device_id,
            device_status=device_status
        )

        stanje = get_stanje(db, device_id)

        data = base.model_dump() if hasattr(base, "model_dump") else dict(base)
        data["status"] = device_status.get("status")
        data["recognition_running"] = (stanje["recognition_running"] if stanje else False)
        #data["camera_on"] = (stanje.get("camera_on", False) if stanje else False)
        data["mode"] = (stanje["mode"] if stanje else None)
        data["last_seen"] = (stanje["last_seen"] if stanje else None)

        return data

    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))