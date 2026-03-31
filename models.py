from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid
from datetime import datetime

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_name = Column(String, nullable=False)
    incident_type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String, nullable=False)
    assigned_unit = Column(String, nullable=True)
    assigned_unit_type = Column(String, nullable=True)
    status = Column(String, default="created")
    timestamp = Column(DateTime, default=datetime.utcnow)