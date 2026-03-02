from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Any, Dict
from fastapi.encoders import jsonable_encoder
from app.db.uredjaj_state_crud import get_state

from app.db import crud
from app.services.stanje_store import get_stanje

ALLOWED_TYPES = {"plastic", "metal", "cardboard"}


def handle_waste_event(
    db: Session,
    device_id: str,
    waste_type: str,
    timestamp: Optional[datetime] = None
):
    """
    Upisuje detekciju otpada u bazu.
    """
    if waste_type not in ALLOWED_TYPES:
        raise ValueError(f"Unknown waste type: {waste_type}")

    crud.insert_waste_event(
        db=db,
        device_id=device_id,
        tip_otpada=waste_type,
        vreme_detekcije=timestamp
    )


from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Any, Dict

from app.db import crud
from app.db.uredjaj_state_crud import get_state  # ovo dodaj (putanja kako si nazvala CRUD)

def build_status_response(
    db: Session,
    device_id: str,
    device_status: Dict[str, Any],
) -> dict:
    counts = crud.get_counts_by_device(db, device_id=device_id)
    for k in ["plastic", "metal", "cardboard"]:
        counts.setdefault(k, 0)

    # 1) STATE IZ BAZE (umesto RAM-a)
    state = get_state(db, device_id)
    mode = state.mode if state else None
    last_seen = state.last_seen if state else None

    # 2) očisti/enkoduj IoT response (da nema Azure SDK objekata)
    device_status = jsonable_encoder(device_status)

    twin = device_status.get("twin") or {}
    status_str = twin.get("status")  # "enabled" / "disabled" / ...

    return {
        "device_id": device_id,
        "status": status_str or "unknown",
        "counts": counts,
        "mode": mode,
        "last_seen": last_seen,
    }