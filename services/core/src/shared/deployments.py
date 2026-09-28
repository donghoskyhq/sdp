from dataclasses import dataclass


class DeploymentError(RuntimeError):
    """A safe-to-log deployment provider error."""


@dataclass(frozen=True)
class DeploymentResult:
    project_id: str
    deployment_id: str
    deployment_url: str
    project_url: str
    service_id: str | None = None
