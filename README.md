# IoT Reciklomat — Backend

Backend for a smart waste-sorting system. A device (Raspberry Pi + camera) detects the type of waste (paper, plastic, glass) using a YOLO model as items pass through the frame, sends the event to the cloud, and the backend logs and aggregates that data for display on a web dashboard.

## Architecture

The system consists of three layers:

1. **Edge Layer** (Raspberry Pi) — waste type detection using a YOLO model
2. **Cloud Gateway** (Azure IoT Hub) — communication between the device and the backend
3. **Presentation Layer** (Web App) — displays aggregated data to the user

The backend is the central control layer, tying together the IoT device, cloud infrastructure, and web application.

## Backend structure

- **api/routes/** — API layer: entry point of the system, forwards requests (`control.py`, `devices.py`, `iothub.py`, `otpad.py`, `stanje.py`, `status.py`)
- **core/** — configuration and security (`config.py`, `security.py`)
- **services/** — Service layer: business logic, combines IoT Hub and database data (`iot_service.py`, `otpad_service.py`, `stanje_store.py`)
- **db/** — Data layer: database communication (`crud.py`, `database.py`, `uredjaj_state_crud.py`)
- **models/** — `db_models.py` (table structure), `schemas.py` (API response structure)
- **main.py** — application entry point

**API layer** — contains no business logic, only forwards requests.
**Service layer** — the heart of the backend: decides what needs to happen, combines data from IoT Hub and the database, implements business rules.
**Data layer** — communicates with the Azure SQL database (connection, CRUD operations, table structure).

## Data flow

1. The device sends a JSON message with the waste type and timestamp to Azure IoT Hub.
2. The backend picks up that event.
3. The service layer processes the data and decides what needs to happen.
4. The data is written to the database as a new detection.
5. Device state is updated if needed.
6. The API layer lets the frontend fetch the updated data.

## Azure integration

- **Azure IoT Hub** — device registration, device↔cloud communication, telemetry and direct method commands
- **Azure App Service** — hosts the FastAPI backend, runs the API routes, stores environment variables (IoT Hub connection string, DB connection string)
- **Azure SQL Database** — stores detection and device state data
- **Azure Storage (Static Website)** — hosts the frontend application

## Tech stack

Python, FastAPI, Azure IoT Hub, Azure SQL Database

## Related repositories

- Frontend: [iot-frontend](https://github.com/plavamenta/iot-frontend)

## Team


Project built for the Internet of Things course.

- **Neda Kovačević** — backend and Azure integration
- **Ana Karajović** — frontend
- **Mihailo Marković** — YOLO model integration and Raspberry Pi device
