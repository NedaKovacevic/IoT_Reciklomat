from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import DEVICE_ID_DEFAULT
from app.models.schemas import StatusOut
from app.services.iot_service import get_device_status
from app.services.otpad_service import build_status_response

router = APIRouter(tags=["status"])


@router.get("/status", response_model=StatusOut)
def status(device_id: str = DEVICE_ID_DEFAULT, db: Session = Depends(get_db)):
    device_status = get_device_status(device_id)
    return build_status_response(
        db=db,
        device_id=device_id,
        device_status=device_status
    )
