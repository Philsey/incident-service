from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import Incident
from schemas import IncidentCreate, IncidentResponse, StatusUpdate, AssignUpdate
from typing import List
import math

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Incident Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded responders for testing
RESPONDERS = [
    {"id": "police-1", "name": "Accra Central Police", "type": "police", "latitude": 5.5502, "longitude": -0.2174, "available": True},
    {"id": "police-2", "name": "Lapaz Police Station", "type": "police", "latitude": 5.6037, "longitude": -0.2466, "available": True},
    {"id": "fire-1", "name": "Accra Fire Service", "type": "fire", "latitude": 5.5481, "longitude": -0.2090, "available": True},
    {"id": "fire-2", "name": "Tema Fire Service", "type": "fire", "latitude": 5.6698, "longitude": -0.0166, "available": True},
    {"id": "ambulance-1", "name": "Korle Bu Ambulance", "type": "ambulance", "latitude": 5.5364, "longitude": -0.2279, "available": True},
    {"id": "ambulance-2", "name": "37 Military Hospital Ambulance", "type": "ambulance", "latitude": 5.5731, "longitude": -0.1761, "available": True},
]

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_nearest_responder(incident_type, lat, lon):
    if incident_type.lower() in ["robbery", "crime", "assault", "theft"]:
        responder_type = "police"
    elif incident_type.lower() in ["fire", "explosion"]:
        responder_type = "fire"
    else:
        responder_type = "ambulance"

    available = [r for r in RESPONDERS if r["type"] == responder_type and r["available"]]
    if not available:
        return None

    nearest = min(available, key=lambda r: calculate_distance(lat, lon, r["latitude"], r["longitude"]))
    return nearest

@app.post("/incidents", response_model=IncidentResponse)
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    responder = get_nearest_responder(incident.incident_type, incident.latitude, incident.longitude)
    
    new_incident = Incident(
        citizen_name=incident.citizen_name,
        incident_type=incident.incident_type,
        latitude=incident.latitude,
        longitude=incident.longitude,
        notes=incident.notes,
        created_by=incident.created_by,
        assigned_unit=responder["name"] if responder else None,
        assigned_unit_type=responder["type"] if responder else None,
        status="dispatched" if responder else "created"
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident

@app.get("/incidents/open", response_model=List[IncidentResponse])
def get_open_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).filter(Incident.status != "resolved").all()

@app.get("/incidents/{id}", response_model=IncidentResponse)
def get_incident(id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@app.put("/incidents/{id}/status", response_model=IncidentResponse)
def update_status(id: str, update: StatusUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = update.status
    db.commit()
    db.refresh(incident)
    return incident

@app.put("/incidents/{id}/assign", response_model=IncidentResponse)
def assign_unit(id: str, update: AssignUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.assigned_unit = update.assigned_unit
    incident.assigned_unit_type = update.assigned_unit_type
    db.commit()
    db.refresh(incident)
    return incident