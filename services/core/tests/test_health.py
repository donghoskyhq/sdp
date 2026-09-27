from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "sdp-api",
        "version": "0.1.0",
    }


def test_v1_status() -> None:
    response = client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "configured"
    assert response.json()["redis"] == "configured"
