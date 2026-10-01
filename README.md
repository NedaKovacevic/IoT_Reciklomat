# IoT Reciklomat — Backend

Backend for a smart waste-sorting system. A device (Raspberry Pi + camera) detects the type of waste (plastic, glass, cardboard) using a YOLO model as items pass through the frame and reports each detection to the backend. The backend stores detections in Azure SQL, tracks device state, controls the device remotely through Azure IoT Hub, and serves aggregated data to a web dashboard.

## Architecture

The system consists of three layers:

1. **Edge layer** (Raspberry Pi) — waste type detection using a YOLO model
2. **Backend** (FastAPI on Azure App Service) — receives detection events, stores data, controls devices
3. **Presentation layer** (web app on Azure Storage static website) — dashboard with counts and device status

Azure IoT Hub is used as the device management and control channel: device registry, connection status, and cloud-to-device commands (direct methods).

## Data flow

**Device → backend (detections and state)**

1. The device detects an item and sends an HTTP `POST /waste-event` with `device_id`, `waste_type` and `timestamp`.
2. The service layer validates the waste type (`plastic`, `glass`, `cardboard`); unknown types are rejected with `400`.
3. The detection is written to the `IstorijaOtpada` table.
4. The device periodically reports its mode via `POST /stanje`; the backend upserts the device state and updates `last_seen`.

**Backend → device (control)**

1. The dashboard calls `POST /start` or `POST /stop` for a device.
2. The backend invokes the `START_RECOGNITION` / `STOP_RECOGNITION` direct method on the device through IoT Hub.
3. Device state in the database is updated only if the device accepts the command (status `200`); otherwise the backend returns `rejected` and the stored state stays unchanged.

**Dashboard → backend (reading data)**

- `GET /status` combines detection counts per waste type (database), device state (database) and device status from the IoT Hub registry.
- `GET /devices` lists devices registered in IoT Hub with their connection state, last activity time and whether recognition is running.

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/waste-event` | Device reports a detected item |
| `POST` | `/stanje` | Device reports its mode (heartbeat) |
| `POST` | `/start` | Start recognition on a device (operator only) |
| `POST` | `/stop` | Stop recognition on a device (operator only) |
| `GET` | `/status` | Counts per waste type and device status |
| `GET` | `/devices` | Devices from the IoT Hub registry with their state |
| `GET` | `/iothub/ping` | Checks the connection to IoT Hub |

## Backend structure

- `app/main.py` — FastAPI app, CORS configuration, router registration
- `app/api/routes/` — API layer, entry point of the system; validates input and forwards requests to services, no business logic
  - `otpad.py` — detection events
  - `stanje.py` — device state reports
  - `control.py` — start/stop commands
  - `status.py` — aggregated status for the dashboard
  - `devices.py` — device list
  - `iothub.py` — IoT Hub connectivity check
- `app/services/` — service layer, business logic; combines data from the database and IoT Hub
  - `otpad_service.py` — validates and stores detections, builds the status response
  - `iot_service.py` — IoT Hub integration (direct methods, device registry)
  - `stanje_store.py` — device state handling
- `app/db/` — data layer, communication with Azure SQL
  - `database.py` — connection and session
  - `crud.py` — detection queries (insert, counts per device)
  - `uredjaj_state_crud.py` — device state upsert
- `app/models/`
  - `db_models.py` — SQLAlchemy table definitions
  - `schemas.py` — Pydantic request/response schemas
- `app/core/`
  - `config.py` — configuration from environment variables
  - `security.py` — operator role check

## Database (Azure SQL)

- `IstorijaOtpada` — detection history: device, waste type, detection time
- `Uredjaji` — device state: mode, last seen, IoT status, whether recognition is running
- `Korisnici` — users with password hash and role

## Azure services

- **Azure IoT Hub** — device registry, connection status, direct method commands
- **Azure App Service** — hosts the FastAPI backend; connection strings are stored as environment variables
- **Azure SQL Database** — detection and device state data
- **Azure Storage (static website)** — hosts the frontend

## Tech stack

Python, FastAPI, SQLAlchemy, Pydantic, pyodbc, Azure IoT Hub SDK (`azure-iot-hub`), Gunicorn/Uvicorn, Azure SQL Database

## Running locally

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables for the IoT Hub service connection string and the database connection string.
3. Start the server: `uvicorn app.main:app --reload`

## Known limitations

- Role check is based on an `X-Role` request header, which is suitable for a prototype only; a production version would use token-based authentication (e.g. JWT or Azure AD) backed by the `Korisnici` table.
- Device endpoints (`/waste-event`, `/stanje`) are not authenticated.

## Related repositories

- Frontend: [iot-frontend](https://github.com/plavamenta/iot-frontend)

## Team

Project built for the Internet of Things course.

- Backend and Azure integration: Neda Kovačević
- Frontend: Ana Karajović
- YOLO model and Raspberry Pi: Mihailo Marković
