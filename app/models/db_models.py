from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.db.database import Base

class IstorijaOtpada(Base):
    __tablename__ = "IstorijaOtpada"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), nullable=False)
    tip_otpada = Column(String(20), nullable=False)
    vreme_detekcije = Column(DateTime, default=datetime.utcnow)

class Korisnici(Base):
    __tablename__ = "Korisnici"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=True)


class UredjajState(Base):
    __tablename__ = "Uredjaji"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, nullable=False, unique=True)
    iot_status = Column(String, nullable=False, default="disabled")
    mode = Column(String, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    recognition_running = Column(Boolean, default=False)

    #camera_on = Column(Boolean, nullable=True)