# app/services/iot_service.py
import os
from typing import Any, Dict, List, Optional

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod
from azure.core.exceptions import AzureError


def _get_iothub_connection_string() -> str:
    """
    Uzima SERVICE connection string za IoT Hub iz env var.
    Ovo nije device connection string, nego "service" koji ima prava da listа uređaje,
    čita njihov status i šalje direct methods.
    """
    cs = os.getenv("IOTHUB_SERVICE_CONNECTION_STRING")
    if not cs:
        raise RuntimeError(
            "Missing env var IOTHUB_SERVICE_CONNECTION_STRING (IoT Hub service connection string)."
        )
    return cs


def _get_registry() -> IoTHubRegistryManager:
    """Kreira registry manager (klijent za IoT Hub identity registry)."""
    return IoTHubRegistryManager(_get_iothub_connection_string())


def _norm_iothub_value(x: Any) -> Any:
    """
    Normalizuje vrednosti koje Azure SDK često vraća kao Enum ili objekte
    (npr. DeviceStatus, DeviceConnectionState) u čiste JSON-friendly vrednosti.

    - Ako postoji .value -> vrati x.value (to je obično "enabled"/"disabled" ili "connected"/"disconnected")
    - Ako je string -> vrati string
    - Inače -> str(x)
    """
    if x is None:
        return None
    if hasattr(x, "value"):
        return getattr(x, "value")
    if isinstance(x, str):
        return x
    return str(x)


# ---------------------------
# Direct methods (C2D)
# ---------------------------

def invoke_direct_method(
    device_id: str,
    method_name: str,
    payload: Optional[Dict[str, Any]] = None,
    response_timeout_in_seconds: int = 30,
    connect_timeout_in_seconds: int = 10,
) -> Dict[str, Any]:
    """
    Poziva direct method na uređaju (Cloud-to-Device Method).
    Uređaj mora da bude online i da ima implementiran handler za method_name.

    Koristi se kod tebe za START_RECOGNITION / STOP_RECOGNITION.
    """
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
    """Wrapper za START_RECOGNITION direct method."""
    return invoke_direct_method(device_id=device_id, method_name="START_RECOGNITION", payload=payload)


def stop_recognition(device_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Wrapper za STOP_RECOGNITION direct method."""
    return invoke_direct_method(device_id=device_id, method_name="STOP_RECOGNITION", payload=payload)


# ---------------------------
# Registry (list/get device)
# ---------------------------

def list_devices_basic(max_devices: int = 100) -> List[Dict[str, Any]]:
    """
    Vraća spisak uređaja iz IoT Hub-a (identity registry) u "basic" formatu
    koji je zgodan za UI:

    - device_id
    - status: "enabled"/"disabled" (ADMIN dozvola za konekciju)
    - connection_state: "connected"/"disconnected" (trenutno stanje konekcije u hub-u)
    - last_activity_time: string ili None (poslednja aktivnost koju hub vidi)

    Bitno:
    - status != online/offline. "enabled" samo znači da mu je dozvoljeno da se konektuje.
    """
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
    """
    Vraća IoT Hub view za jedan device:

    - status: "enabled"/"disabled"
    - connection_state: "connected"/"disconnected"
    - last_activity_time

    Koristi se kod tebe u /status endpointu.
    """
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