from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.models.schemas import ControlIn
from app.services.iot_service import send_command_to_device

router = APIRouter(tags=["control"])

def _require_operator(x_role: Optional[str]):
    if x_role != "operator":
        raise HTTPException(status_code=403, detail="Operator role required")

@router.post("/start")
def start_device(body: ControlIn, x_role: Optional[str] = Header(default=None, alias="X-Role")):
    _require_operator(x_role)
    send_command_to_device(body.device_id, "START")
    return {"status": "ok", "device_id": body.device_id, "command": "START"}

@router.post("/stop")
def stop_device(body: ControlIn, x_role: Optional[str] = Header(default=None, alias="X-Role")):
    _require_operator(x_role)
    send_command_to_device(body.device_id, "STOP")
    return {"status": "ok", "device_id": body.device_id, "command": "STOP"}
