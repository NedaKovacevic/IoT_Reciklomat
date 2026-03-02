# app/services/iot_service.py

import os
from typing import Any, Dict, List, Optional

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod
from azure.core.exceptions import AzureError


def _get_iothub_connection_string() -> str:
    cs = os.getenv("IOTHUB_CONNECTION_STRING")
    if not cs:
        # Namerno jasna poruka da odmah znaš šta fali na Azure
        raise RuntimeError("Missing env var IOTHUB_CONNECTION_STRING (IoT Hub service connection string).")
    return cs


def _get_registry() -> IoTHubRegistryManager:
    return IoTHubRegistryManager(_get_iothub_connection_string())


def send_command_to_device(
    device_id: str,
    method_name: str,
    payload: Optional[Dict[str, Any]] = None,
    response_timeout_in_seconds: int = 30,
    connect_timeout_in_seconds: int = 10,
) -> Dict[str, Any]:
    """
    Invokes an IoT Hub Direct Method on a device.

    Returns a dict with status/payload info to make it JSON serializable.
    """
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

        # resp je objekat (ne dict). Pretvaramo u JSON-friendly format.
        return {
            "device_id": device_id,
            "method": method_name,
            "status": getattr(resp, "status", None),
            "payload": getattr(resp, "payload", None),
        }

    except AzureError as e:
        # Azure SDK error (auth, not found, timeout, itd)
        raise RuntimeError(f"IoT Hub direct method failed: {e}") from e
    except Exception as e:
        # Sve ostalo
        raise RuntimeError(f"Unexpected error invoking direct method: {e}") from e


def start_device(device_id: str) -> Dict[str, Any]:
    return send_command_to_device(device_id=device_id, method_name="START")


def stop_device(device_id: str) -> Dict[str, Any]:
    return send_command_to_device(device_id=device_id, method_name="STOP")


def list_devices(max_devices: int = 100) -> List[Dict[str, Any]]:
    """
    Lists devices registered in IoT Hub (device identity registry).
    """
    registry = _get_registry()
    try:
        devices = registry.get_devices(max_devices)
        # devices je lista objekata - pretvori u JSON-friendly
        out: List[Dict[str, Any]] = []
        for d in devices:
            out.append(
                {
                    "device_id": getattr(d, "device_id", None),
                    "status": getattr(d, "status", None),
                    "connection_state": getattr(d, "connection_state", None),
                    "last_activity_time": str(getattr(d, "last_activity_time", "")) if getattr(d, "last_activity_time", None) else None,
                }
            )
        return out
    except AzureError as e:
        raise RuntimeError(f"Failed to list IoT Hub devices: {e}") from e

def get_device_status(device_id: str) -> Dict[str, Any]:
    """
    Returns IoT Hub device twin (status + properties) for given device_id.
    This satisfies import in app/api/routes/status.py: from app.services.iot_service import get_device_status
    """
    if not device_id:
        raise ValueError("device_id is required")

    registry = _get_registry()

    try:
        twin = registry.get_twin(device_id)

        # SDK nekad vraća JSON string, nekad objekat/dict.
        # Pretvori u JSON-friendly formu.
        if isinstance(twin, str):
            import json
            twin_obj = json.loads(twin)
        else:
            # fallback: pokušaj da uzmeš __dict__ ako je model objekat
            twin_obj = getattr(twin, "__dict__", twin)

        return {
            "device_id": device_id,
            "twin": twin_obj,
        }

    except AzureError as e:
        raise RuntimeError(f"Failed to get device status/twin from IoT Hub: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error getting device status: {e}") from e