# backend/tests/unit/test_traffic_service.py
import pytest
from app.services.traffic_service import TrafficService
from app.models.vehicle import Vehicle
from app.models.incident import Incident, IncidentType, IncidentSeverity

@pytest.mark.asyncio
async def test_create_incident(db_client):
    service = TrafficService(db_client)
    data = {
        "type": IncidentType.ACCIDENT,
        "severity": IncidentSeverity.HIGH,
        "lat": 28.6139,
        "lng": 77.2090,
        "description": "Test incident",
    }
    incident = await service.create_incident(data)
    assert incident.id is not None
    assert incident.type == IncidentType.ACCIDENT
    assert not incident.resolved

@pytest.mark.asyncio
async def test_resolve_incident(db_client):
    service = TrafficService(db_client)
    data = {
        "type": IncidentType.CONGESTION,
        "severity": IncidentSeverity.LOW,
        "lat": 28.6139,
        "lng": 77.2090,
        "description": "Test congestion",
    }
    incident = await service.create_incident(data)
    resolved = await service.resolve_incident(incident.id)
    assert resolved.resolved == True
    assert resolved.end_time is not None