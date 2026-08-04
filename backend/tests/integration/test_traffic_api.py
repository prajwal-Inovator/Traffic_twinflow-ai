# backend/tests/integration/test_traffic_api.py
def test_get_live_traffic(test_client, auth_headers):
    response = test_client.get("/api/v1/traffic/live", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "vehicles" in data["data"] or "signals" in data["data"]

def test_create_incident(test_client, auth_headers):
    response = test_client.post("/api/v1/traffic/incidents", headers=auth_headers, json={
        "type": "accident",
        "severity": "critical",
        "lat": 28.6139,
        "lng": 77.2090,
        "description": "API Test incident"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] is not None