import os
from typing import Any, Dict, List, Optional

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod
from azure.core.exceptions import AzureError


def _get_iothub_connection_string() -> str:
    cs = os.getenv("IOTHUB_SERVICE_CONNECTION_STRING")
    if not cs:
        raise RuntimeError(
            "Missing env var IOTHUB_SERVICE_CONNECTION_STRING (IoT Hub service connection string)."
        )
    return cs


def _get_registry() -> IoTHubRegistryManager:
    return IoTHubRegistryManager(_get_iothub_connection_string())


def _norm_iothub_value(x: Any) -> Any:
    if x is None:
        return None
    if hasattr(x, "value"):
        return getattr(x, "value")
    if isinstance(x, str):
        return x
    return str(x)


# Direktne metode

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
        return {
            "device_id": device_id,
            "method": method_name,
            "status": _norm_iothub_value(getattr(resp, "status", None)),
            "payload": getattr(resp, "payload", None),
        }
    except AzureError as e:
        raise RuntimeError(f"IoT Hub direct method failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error invoking direct method: {e}") from e


def start_recognition(device_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return invoke_direct_method(device_id=device_id, method_name="START_RECOGNITION", payload=payload)


def stop_recognition(device_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return invoke_direct_method(device_id=device_id, method_name="STOP_RECOGNITION", payload=payload)


# Registry (list/get device)

def list_devices_basic(max_devices: int = 100) -> List[Dict[str, Any]]:
    registry = _get_registry()
    try:
        devices = registry.get_devices(max_devices)
        out: List[Dict[str, Any]] = []
        for d in devices:
            out.append(
                {
                    "device_id": _norm_iothub_value(getattr(d, "device_id", None)),
                    "status": _norm_iothub_value(getattr(d, "status", None)),
                    "connection_state": _norm_iothub_value(getattr(d, "connection_state", None)),
                    "last_activity_time": (
                        str(getattr(d, "last_activity_time", None))
                        if getattr(d, "last_activity_time", None)
                        else None
                    ),
                }
            )
        return out
    except AzureError as e:
        raise RuntimeError(f"Failed to list IoT Hub devices: {e}") from e


def get_device_iothub_status(device_id: str) -> Dict[str, Any]:
    if not device_id:
        raise ValueError("device_id is required")

    registry = _get_registry()
    try:
        d = registry.get_device(device_id)
        return {
            "device_id": _norm_iothub_value(getattr(d, "device_id", None)),
            "status": _norm_iothub_value(getattr(d, "status", None)),
            "connection_state": _norm_iothub_value(getattr(d, "connection_state", None)),
            "last_activity_time": (
                str(getattr(d, "last_activity_time", None))
                if getattr(d, "last_activity_time", None)
                else None
            ),
        }
    except AzureError as e:
        raise RuntimeError(f"Failed to get IoT Hub device status: {e}") from e