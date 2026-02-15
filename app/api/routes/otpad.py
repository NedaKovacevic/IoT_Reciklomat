from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.schemas import WasteEventIn
from app.services.otpad_service import handle_waste_event

router = APIRouter(tags=["waste"])


@router.post("/waste-event")
def waste_event(payload: WasteEventIn, db: Session = Depends(get_db)):
    try:
        handle_waste_event(
            db=db,
            device_id=payload.device_id,
            waste_type=payload.waste_type,
            timestamp=payload.timestamp
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok"}
