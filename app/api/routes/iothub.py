from fastapi import APIRouter, HTTPException
from app.core.config import IOT_HUB_CONNECTION_STRING

router = APIRouter(prefix="/iothub", tags=["iothub"])

@router.get("/ping")
def ping_iothub():
    if not IOT_HUB_CONNECTION_STRING:
        raise HTTPException(status_code=500, detail="Missing IOT Hub connection string env var.")
    try:
        from azure.iot.hub import IoTHubRegistryManager
        reg = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)
        # “lagan” poziv – uzmi prvih par uređaja
        devs = reg.get_devices(5)
        return [{"device_id": d.device_id, "status": getattr(d, "status", None)} for d in devs]
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))