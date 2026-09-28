from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from api.v1 import projects as projects_api
from shared.database import Base, get_db


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db() -> Iterator[Session]:
        with testing_session() as session:
            yield session

    monkeypatch.setattr(projects_api, "enqueue_project_provisioning", lambda _project_id: "job-1")
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def test_create_and_list_project(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Customer Portal",
            "repository_name": "customer-portal",
            "description": "Customer self-service site",
        },
    )

    assert response.status_code == 202
    assert response.json()["status"] == "pending"
    assert response.json()["repository_name"] == "customer-portal"

    listed = client.get("/api/v1/projects")
    assert listed.status_code == 200
    assert [project["name"] for project in listed.json()] == ["Customer Portal"]


def test_duplicate_repository_name_is_rejected(client: TestClient) -> None:
    payload = {"name": "First", "repository_name": "shared-repo"}
    assert client.post("/api/v1/projects", json=payload).status_code == 202

    duplicate = client.post(
        "/api/v1/projects",
        json={"name": "Second", "repository_name": "shared-repo"},
    )

    assert duplicate.status_code == 409


def test_invalid_repository_name_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects",
        json={"name": "Invalid", "repository_name": "not/allowed"},
    )

    assert response.status_code == 422

    uppercase = client.post(
        "/api/v1/projects",
        json={"name": "Invalid", "repository_name": "Not-Lowercase"},
    )
    assert uppercase.status_code == 422
