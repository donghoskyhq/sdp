import logging

from shared.config import get_settings
from shared.database import SessionLocal
from shared.github import GitHubClient
from shared.models import Project

logger = logging.getLogger(__name__)


def provision_project(project_id: str) -> dict[str, str]:
    """Create a GitHub repository and seed it with the approved Next.js starter."""
    logger.info("Received provision_project job", extra={"project_id": project_id})
    settings = get_settings()

    try:
        with SessionLocal() as session:
            project = session.get(Project, project_id)
            if project is None:
                raise ValueError(f"Project {project_id} does not exist")
            if project.status == "ready" and project.github_url:
                return {"project_id": project_id, "status": "ready"}

            project.status = "provisioning"
            project.error_message = None
            session.commit()

            with GitHubClient.from_settings(settings) as github:
                repository = github.create_nextjs_repository(
                    name=project.repository_name,
                    project_name=project.name,
                    description=project.description,
                    private=settings.github_repository_private,
                )

            project.status = "ready"
            project.github_url = repository.html_url
            project.github_full_name = repository.full_name
            session.commit()
    except Exception as exc:
        logger.exception("Project provisioning failed", extra={"project_id": project_id})
        with SessionLocal() as session:
            project = session.get(Project, project_id)
            if project is not None:
                project.status = "failed"
                project.error_message = str(exc)[:1000]
                session.commit()
        raise

    logger.info("Completed provision_project job", extra={"project_id": project_id})
    return {"project_id": project_id, "status": "ready"}
