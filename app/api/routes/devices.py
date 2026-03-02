from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.iot_service import list_devices
from app.db.uredjaj_state_crud import list_states  # ako si ga tako nazvala

router = APIRouter(tags=["devices"])


@router.get("/devices")
def devices(db: Session = Depends(get_db)):
    # IoT Hub: enabled/disabled lista uređaja
    hub_devices = list_devices(max_devices=200)

    # DB: mode/last_seen iz dbo.Uredjaji
    states = list_states(db)
    states_map = {s.device_id: s for s in states}

    out = []
    for d in hub_devices:
        device_id = d.get("device_id")
        state = states_map.get(device_id)

        out.append(
            {
                "device_id": device_id,
                "status": str(d.get("status") or "unknown"),   # enabled/disabled
                "mode": state.mode if state else None,
                "last_seen": state.last_seen.isoformat() if (state and state.last_seen) else None,
            }
        )

    return out