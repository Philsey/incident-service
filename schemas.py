from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class IncidentCreate(BaseModel):
    citizen_name: str
    incident_type: str
    latitude: float
    longitude: float
    notes: Optional[str] = None
    created_by: str

class IncidentResponse(BaseModel):
    id: UUID
    citizen_name: str
    incident_type: str
    latitude: float
    longitude: float
    notes: Optional[str] = None
    created_by: str
    assigned_unit: Optional[str] = None
    assigned_unit_type: Optional[str] = None
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str

class AssignUpdate(BaseModel):
    assigned_unit: str
    assigned_unit_type: str