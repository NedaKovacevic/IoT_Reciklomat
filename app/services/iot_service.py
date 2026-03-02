import os
from typing import Any, Dict, List, Optional

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod
from azure.core.exceptions import AzureError

# Memorija za ON/OFF status (dok Pi ne posalje komandu)
_DEVICE_STATUS: Dict[str, str] = {}


def _get_iothub_connection_string() -> str:
    cs = os.getenv("IOTHUB_SERVICE_CONNECTION_STRING")
    if not cs:
        raise RuntimeError("Missing env var IOTHUB_SERVICE_CONNECTION_STRING")
    return cs


def _get_registry() -> IoTHubRegistryManager:
    return IoTHubRegistryManager(_get_iothub_connection_string())


def set_device_status(device_id: str, status: str) -> None:
    _DEVICE_STATUS[device_id] = status


def get_device_status(device_id: str) -> str:
    """Vraca ON/OFF string iz memorije. StatusOut schema ocekuje string."""
    return _DEVICE_STATUS.get(device_id, "OFF")


def send_command_to_device(
    device_id: str,
    method_name: str,
    payload: Optional[Dict[str, Any]] = None,
    response_timeout_in_seconds: int = 30,
    connect_timeout_in_seconds: int = 10,
) -> Dict[str, Any]:
    if not device_id:
        raise ValueError("device_id is required")
    if not method_name:
        raise ValueError("method_name is required")

    registry = _get_registry()

    direct_method = CloudToDeviceMethod(
        method_name=method_name,
        payload=payload or {"source": "backend"},
        response_timeout_in_seconds=response_timeout_in_seconds,
        connect_timeout_in_seconds=connect_timeout_in_seconds,
    )

    try:
        resp = registry.invoke_device_method(device_id, direct_method)

        # Azuriraj memoriju
        if method_name.upper() == "START":
            set_device_status(device_id, "ON")
        elif method_name.upper() == "STOP":
            set_device_status(device_id, "OFF")

        return {
            "device_id": device_id,
            "method": method_name,
            "status": getattr(resp, "status", None),
            "payload": getattr(resp, "payload", None),
        }

    except AzureError as e:
        raise RuntimeError(f"IoT Hub direct method failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error invoking direct method: {e}") from e


def start_device(device_id: str) -> Dict[str, Any]:
    return send_command_to_device(device_id=device_id, method_name="START")


def stop_device(device_id: str) -> Dict[str, Any]:
    return send_command_to_device(device_id=device_id, method_name="STOP")


def list_devices(max_devices: int = 100) -> List[Dict[str, Any]]:
    registry = _get_registry()
    try:
        devices = registry.get_devices(max_devices)
        out: List[Dict[str, Any]] = []
        for d in devices:
            out.append({
                "device_id": getattr(d, "device_id", None),
                "status": getattr(d, "status", None),
                "connection_state": getattr(d, "connection_state", None),
                "last_activity_time": str(getattr(d, "last_activity_time", "")) if getattr(d, "last_activity_time", None) else None,
            })
        return out
    except AzureError as e:
        raise RuntimeError(f"Failed to list IoT Hub devices: {e}") from e