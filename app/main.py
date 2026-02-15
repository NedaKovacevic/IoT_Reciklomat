from fastapi import FastAPI
from app.api.routes.otpad import router as otpad_router
from app.api.routes.status import router as status_router
from app.api.routes.control import router as control_router
from app.api.routes.stanje import router as stanje_router


app = FastAPI(title="Recycling Backend")



app.include_router(otpad_router)
app.include_router(status_router)
app.include_router(control_router)
app.include_router(stanje_router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # MVP: svuda dozvoli (posle zakljucas na domen webapp-a)
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"service": "reciklomat-backend", "ok": True}
#komentar lalalala

