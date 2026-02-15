from fastapi import FastAPI
from app.api.routes.otpad import router as otpad_router
from app.api.routes.status import router as status_router
from app.api.routes.control import router as control_router
from app.api.routes.stanje import router as stanje_router


app = FastAPI(title="Recycling Backend")

@app.get("/")
def root():
    return {"message": "Backend is running"}

app.include_router(otpad_router)
app.include_router(status_router)
app.include_router(control_router)
app.include_router(stanje_router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://reciklomat-g7e2h9gvanbdevfx.switzerlandnorth-01.azurewebsites.net"],          # MVP: svuda dozvoli (posle zakljucas na domen webapp-a)
    allow_methods=["https://reciklomat-g7e2h9gvanbdevfx.switzerlandnorth-01.azurewebsites.net"],
    allow_headers=["https://reciklomat-g7e2h9gvanbdevfx.switzerlandnorth-01.azurewebsites.net"],
)
@app.get("/")
def root():
    return {"service": "reciklomat-backend", "ok": True}
#komentar lalalala

