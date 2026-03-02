# app/models/uredjaj_state.py

from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.db.database import Base
from sqlalchemy import Boolean


class UredjajState(Base):
    __tablename__ = "Uredjaji"
    __table_args__ = {"schema": "dbo"}  # Azure SQL default schema

    device_id = Column(String(128), primary_key=True, index=True)
    mode = Column(String(32), nullable=False)
    last_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    #camera_on = Column(Boolean, nullable=True)





# u klasi UredjajState, pored recognition_running:

