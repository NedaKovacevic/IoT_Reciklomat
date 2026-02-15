from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models.db_models import IstorijaOtpada

def insert_waste_event(db: Session, device_id: str, tip_otpada: str, vreme_detekcije=None):
    zapis = IstorijaOtpada(
        device_id=device_id,
        tip_otpada=tip_otpada,
        vreme_detekcije=vreme_detekcije or datetime.utcnow()
    )
    db.add(zapis)
    db.commit()
    db.refresh(zapis)
    return zapis

def get_counts_by_device(db: Session, device_id: str) -> dict[str, int]:
    rows = (
        db.query(IstorijaOtpada.tip_otpada, func.count(IstorijaOtpada.id))
        .filter(IstorijaOtpada.device_id == device_id)
        .group_by(IstorijaOtpada.tip_otpada)
        .all()
    )
    return {tip: cnt for tip, cnt in rows}

def get_recent_events(db: Session, device_id: str, limit: int = 10):
    rows = (
        db.query(IstorijaOtpada.device_id, IstorijaOtpada.tip_otpada, IstorijaOtpada.vreme_detekcije)
        .filter(IstorijaOtpada.device_id == device_id)
        .order_by(IstorijaOtpada.vreme_detekcije.desc())
        .limit(limit)
        .all()
    )
    return [{"device_id": r[0], "tip_otpada": r[1], "vreme_detekcije": r[2]} for r in rows]
