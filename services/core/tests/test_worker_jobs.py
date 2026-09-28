from collections.abc import Iterator
from contextlib import AbstractContextManager

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from shared.database import Base
from shared.deployments import DeploymentResult
from shared.github import GitHubRepository
from shared.models import Project
from worker import jobs


class FakeGitHubClient(AbstractContextManager["FakeGitHubClient"]):
    def __enter__(self) -> "FakeGitHubClient":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def create_nextjs_repository(self, **_kwargs: object) -> GitHubRepository:
        return GitHubRepository(
            id=123456,
            full_name="sky/example-project",
            html_url="https://github.com/sky/example-project",
            default_branch="main",
        )


class FakeVercelClient(AbstractContextManager["FakeVercelClient"]):
    def __enter__(self) -> "FakeVercelClient":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def deploy_github_repository(self, **_kwargs: object) -> DeploymentResult:
        return DeploymentResult(
            project_id="prj_vercel",
            deployment_id="dpl_vercel",
            deployment_url="https://example-project.vercel.app",
            project_url="https://vercel.com/dashboard",
        )


class FakeRailwayClient(AbstractContextManager["FakeRailwayClient"]):
    def __enter__(self) -> "FakeRailwayClient":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def deploy_github_repository(self, **_kwargs: object) -> DeploymentResult:
        return DeploymentResult(
            project_id="prj_railway",
            service_id="svc_railway",
            deployment_id="dpl_railway",
            deployment_url="https://example-project.up.railway.app",
            project_url="https://railway.com/project/prj_railway",
        )


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, expire_on_commit=False)
    engine.dispose()


@pytest.mark.parametrize(
    ("target", "client_name", "fake_client", "expected_url"),
    [
        ("vercel", "VercelClient", FakeVercelClient, "https://example-project.vercel.app"),
        (
            "railway",
            "RailwayClient",
            FakeRailwayClient,
            "https://example-project.up.railway.app",
        ),
    ],
)
def test_provision_project_creates_repository_and_deployment(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: sessionmaker[Session],
    target: str,
    client_name: str,
    fake_client: type[object],
    expected_url: str,
) -> None:
    project = Project(
        name="Example", repository_name="example-project", deployment_target=target
    )
    with session_factory() as session:
        session.add(project)
        session.commit()
        project_id = project.id

    monkeypatch.setattr(jobs, "SessionLocal", session_factory)
    monkeypatch.setattr(
        jobs.GitHubClient,
        "from_settings",
        lambda _settings: FakeGitHubClient(),
    )
    monkeypatch.setattr(
        getattr(jobs, client_name),
        "from_settings",
        lambda _settings: fake_client(),
    )

    result = jobs.provision_project(project_id)

    assert result == {"project_id": project_id, "status": "ready"}
    with session_factory() as session:
        stored = session.get(Project, project_id)
        assert stored is not None
        assert stored.status == "ready"
        assert stored.github_full_name == "sky/example-project"
        assert stored.github_url == "https://github.com/sky/example-project"
        assert stored.deployment_target == target
        assert stored.deployment_url == expected_url
        assert stored.deployment_id is not None
