# app/services/iot_service.py

from __future__ import annotations
from typing import Dict

from app.core.config import IOT_HUB_CONNECTION_STRING

# Fallback memorija (lokalno testiranje bez IoT Hub-a)
_DEVICE_STATUS: Dict[str, str] = {}

def set_device_status(device_id: str, status: str) -> None:
    _DEVICE_STATUS[device_id] = status

def get_device_status(device_id: str) -> str:
    return _DEVICE_STATUS.get(device_id, "OFF")

def _fallback_command(device_id: str, command: str) -> None:
    if command == "START":
        set_device_status(device_id, "ON")
    elif command == "STOP":
        set_device_status(device_id, "OFF")

def send_command_to_device(device_id: str, command: str) -> None:
    """
    Produkcija: šalje komandu uređaju preko Azure IoT Hub Direct Methods.
    Fallback: ako nema IOT_HUB_CONNECTION_STRING, radi kao pre (memorija).
    """
    if not IOT_HUB_CONNECTION_STRING:
        _fallback_command(device_id, command)
        return

    # Import ovde da lokalno ne puca ako nema dependency
    from azure.iot.hub import IoTHubRegistryManager

    registry = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)

    # Mapiranje komandi -> direct method imena (dogovor sa Mihailom)
    if command == "START":
        method_name = "start"
    elif command == "STOP":
        method_name = "stop"
    else:
        raise ValueError(f"Nepoznata komanda: {command}")

    # Pozovi direct method
    resp = registry.invoke_device_method(device_id, {
        "methodName": method_name,
        "payload": {"source": "backend"},
        "responseTimeoutInSeconds": 30
    })

    # Ako hoćeš, možeš ovde da update-uješ i lokalni status za UI
    # (UI će svakako čitati status iz tvoje baze/status endpointa)
    if command == "START":
        set_device_status(device_id, "ON")
    else:
        set_device_status(device_id, "OFF")

    # Možeš da dodaš log/print, ali u App Service bolje kroz logging