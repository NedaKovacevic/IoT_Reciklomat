import os
from pathlib import Path
from dotenv import load_dotenv

# root folder je: backend/
ROOT_DIR = Path(__file__).resolve().parents[2]

# ti imas fajl: backend/dbURL.env
ENV_PATH = ROOT_DIR / "dbURL.env"
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL nije postavljen. Proveri fajl: {ENV_PATH}")

IOT_HUB_CONNECTION_STRING = os.getenv("IOT_HUB_CONNECTION_STRING", "")
DEVICE_ID_DEFAULT = os.getenv("DEVICE_ID_DEFAULT", "uredjaj1")
