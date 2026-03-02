# app/services/iot_service.py
import os
from typing import Any, Dict, List, Optional

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod
from azure.core.exceptions import AzureError


def _get_iothub_connection_string() -> str:
    cs = os.getenv("IOTHUB_SERVICE_CONNECTION_STRING")
    if not cs:
        raise RuntimeError("Missing env var IOTHUB_SERVICE_CONNECTION_STRING (IoT Hub service connection string).")
    return cs


def _get_registry() -> IoTHubRegistryManager:
    return IoTHubRegistryManager(_get_iothub_connection_string())


def invoke_direct_method(
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
        payload=payload or {},
        response_timeout_in_seconds=response_timeout_in_seconds,
        connect_timeout_in_seconds=connect_timeout_in_seconds,
    )

    try:
        resp = registry.invoke_device_method(device_id, direct_method)
        # resp.status može biti int ili string, zavisi od SDK-a – normalizuj u str radi JSON-a
        return {
            "device_id": device_id,
            "method": method_name,
            "status": str(getattr(resp, "status", "")),
            "payload": getattr(resp, "payload", None),
        }

    except AzureError as e:
        # Ovde često upadne "Not Found" kad uređaj nema handler za metodu
        raise RuntimeError(f"IoT Hub direct method failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error invoking direct method: {e}") from e


def start_recognition(device_id: str) -> Dict[str, Any]:
    # Ime metode mora da se poklopi sa onim što Mihailo sluša na uređaju.
    # Ako on očekuje npr "START_RECOGNITION", promeni ovde ili napravi env.
    return invoke_direct_method(device_id=device_id, method_name="START")


def stop_recognition(device_id: str) -> Dict[str, Any]:
    return invoke_direct_method(device_id=device_id, method_name="STOP")


def list_devices_basic(max_devices: int = 100) -> List[Dict[str, Any]]:
    registry = _get_registry()
    try:
        devices = registry.get_devices(max_devices)
        out: List[Dict[str, Any]] = []
        for d in devices:
            out.append(
                {
                    "device_id": getattr(d, "device_id", None),
                    "status": getattr(d, "status", None),  # enabled/disabled (IoT Hub)
                    "connection_state": getattr(d, "connection_state", None),
                    "last_activity_time": (
                        str(getattr(d, "last_activity_time", None)) if getattr(d, "last_activity_time", None) else None
                    ),
                }
            )
        return out
    except AzureError as e:
        raise RuntimeError(f"Failed to list IoT Hub devices: {e}") from e


def get_device_iothub_status(device_id: str) -> Dict[str, Any]:
    """Vraća IoT Hub view: enabled/disabled, connection_state, last_activity_time."""
    if not device_id:
        raise ValueError("device_id is required")

    registry = _get_registry()
    try:
        d = registry.get_device(device_id)
        return {
            "device_id": getattr(d, "device_id", None),
            "status": getattr(d, "status", None),  # enabled/disabled
            "connection_state": getattr(d, "connection_state", None),
            "last_activity_time": (
                str(getattr(d, "last_activity_time", None)) if getattr(d, "last_activity_time", None) else None
            ),
        }
    except AzureError as e:
        raise RuntimeError(f"Failed to get IoT Hub device status: {e}") from e