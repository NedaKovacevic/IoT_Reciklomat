from fastapi import FastAPI
from app.api.routes.otpad import router as otpad_router
from app.api.routes.status import router as status_router
from app.api.routes.control import router as control_router
from app.api.routes.stanje import router as stanje_router
from app.api.routes.iothub import router as iothub_router
from app.api.routes.devices import router as devices_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Recycling Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5177",
        "https://frontendreciklomat.z1.web.core.windows.net/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(otpad_router)
app.include_router(status_router)
app.include_router(control_router)
app.include_router(stanje_router)
app.include_router(iothub_router)
app.include_router(devices_router)






@app.get("/")
def root():
    return {"service": "reciklomat-backend", "ok": True}
#komentar lalalala

