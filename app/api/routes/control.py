from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.iot_service import start_device, stop_device

router = APIRouter(tags=["control"])


class DeviceControlRequest(BaseModel):
    device_id: str = Field(..., min_length=1, description="IoT device id, npr. 'uredjaj1'")


@router.post("/start")
def start_device_endpoint(body: DeviceControlRequest):
    """
    Sends START direct method to device via IoT Hub.
    """
    try:
        result = start_device(body.device_id)
        return {"ok": True, "result": result}
    except ValueError as e:
        # loš input
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # IoT Hub / config / auth / device not found / timeout...
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        # nepredviđeno
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.post("/stop")
def stop_device_endpoint(body: DeviceControlRequest):
    """
    Sends STOP direct method to device via IoT Hub.
    """
    try:
        result = stop_device(body.device_id)
        return {"ok": True, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")