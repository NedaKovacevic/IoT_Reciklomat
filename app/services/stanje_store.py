from datetime import datetime, timezone
from typing import Dict, Any

# device_id -> info
_STORE: Dict[str, Dict[str, Any]] = {}

def set_stanje(device_id: str, mode: str):
    _STORE[device_id] = {
        "device_id": device_id,
        "mode": mode,
        "last_seen": datetime.now(timezone.utc)
    }

def get_stanje(device_id: str):
    return _STORE.get(device_id)

def get_all_devices():
    return list(_STORE.values())
