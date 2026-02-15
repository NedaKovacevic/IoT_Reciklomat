# Kasnije: ovde ide Azure IoT Hub Service SDK za slanje cloud-to-device komandi.
# Za MVP (dok nema Pi): cuvamo status u memoriji.

_DEVICE_STATUS: dict[str, str] = {}

def set_device_status(device_id: str, status: str) -> None:
    _DEVICE_STATUS[device_id] = status

def get_device_status(device_id: str) -> str:
    return _DEVICE_STATUS.get(device_id, "OFF")

def send_command_to_device(device_id: str, command: str) -> None:
    """
    Kasnije: stvarno slanje komande preko IoT Hub-a.
    Sada: samo zapamtimo status.
    """
    if command == "START":
        set_device_status(device_id, "ON")
    elif command == "STOP":
        set_device_status(device_id, "OFF")
