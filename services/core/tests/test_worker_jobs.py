from collections.abc import Iterator
from contextlib import AbstractContextManager

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from shared.database import Base
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
            full_name="sky/example-project",
            html_url="https://github.com/sky/example-project",
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


def test_provision_project_creates_repository(
    monkeypatch: pytest.MonkeyPatch, session_factory: sessionmaker[Session]
) -> None:
    project = Project(name="Example", repository_name="example-project")
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

    result = jobs.provision_project(project_id)

    assert result == {"project_id": project_id, "status": "ready"}
    with session_factory() as session:
        stored = session.get(Project, project_id)
        assert stored is not None
        assert stored.status == "ready"
        assert stored.github_full_name == "sky/example-project"
        assert stored.github_url == "https://github.com/sky/example-project"
