import re
import time
from typing import Any

import httpx

from shared.config import Settings
from shared.deployments import DeploymentError, DeploymentResult


class VercelClient:
    def __init__(
        self,
        *,
        token: str,
        team_id: str = "",
        api_url: str = "https://api.vercel.com",
        poll_interval_seconds: float = 5.0,
        timeout_seconds: int = 900,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not token:
            raise DeploymentError("Vercel provisioning is not configured")

        self.team_id = team_id
        self.poll_interval_seconds = poll_interval_seconds
        self.timeout_seconds = timeout_seconds
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=api_url.rstrip("/"),
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "sky-dev-platform",
            },
        )

    @classmethod
    def from_settings(cls, settings: Settings) -> "VercelClient":
        return cls(
            token=settings.vercel_token,
            team_id=settings.vercel_team_id,
            api_url=settings.vercel_api_url,
            poll_interval_seconds=settings.deployment_poll_interval_seconds,
            timeout_seconds=settings.deployment_timeout_seconds,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "VercelClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def deploy_github_repository(
        self,
        *,
        repository_id: int,
        repository_full_name: str,
        repository_name: str,
        branch: str,
    ) -> DeploymentResult:
        project_name = self._project_name(repository_name)
        project = self._request(
            "POST",
            "/v11/projects",
            expected_statuses={200, 201},
            json={
                "name": project_name,
                "framework": "nextjs",
                "gitRepository": {"type": "github", "repo": repository_full_name},
            },
        )
        project_id = self._required_string(project, "id")

        deployment = self._request(
            "POST",
            "/v13/deployments",
            expected_statuses={200, 201},
            json={
                "name": project_name,
                "project": project_id,
                "target": "production",
                "gitSource": {
                    "type": "github",
                    "repoId": repository_id,
                    "ref": branch,
                },
            },
        )
        deployment_id = self._required_string(deployment, "id")
        completed = self._wait_for_deployment(deployment_id, initial=deployment)
        deployment_host = self._required_string(completed, "url")
        deployment_url = (
            deployment_host
            if deployment_host.startswith(("http://", "https://"))
            else f"https://{deployment_host}"
        )

        return DeploymentResult(
            project_id=project_id,
            deployment_id=deployment_id,
            deployment_url=deployment_url,
            project_url="https://vercel.com/dashboard",
        )

    def _wait_for_deployment(
        self, deployment_id: str, *, initial: dict[str, Any]
    ) -> dict[str, Any]:
        deadline = time.monotonic() + self.timeout_seconds
        deployment = initial
        while True:
            ready_state = deployment.get("readyState")
            if ready_state == "READY":
                return deployment
            if ready_state in {"ERROR", "CANCELED"}:
                message = deployment.get("errorMessage")
                detail = message if isinstance(message, str) and message else ready_state
                raise DeploymentError(f"Vercel deployment failed: {detail}")
            if time.monotonic() >= deadline:
                raise DeploymentError("Vercel deployment timed out")

            time.sleep(self.poll_interval_seconds)
            deployment = self._request(
                "GET",
                f"/v13/deployments/{deployment_id}",
                expected_statuses={200},
            )

    def _request(
        self,
        method: str,
        path: str,
        *,
        expected_statuses: set[int],
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = {"teamId": self.team_id} if self.team_id else None
        try:
            response = self._client.request(method, path, params=params, json=json)
        except httpx.HTTPError as exc:
            raise DeploymentError("Vercel could not be reached") from exc

        if response.status_code not in expected_statuses:
            message = "request failed"
            try:
                body = response.json()
                error = body.get("error") if isinstance(body, dict) else None
                if isinstance(error, dict) and isinstance(error.get("message"), str):
                    message = error["message"]
            except ValueError:
                pass
            raise DeploymentError(f"Vercel API returned {response.status_code}: {message}")

        body = response.json()
        if not isinstance(body, dict):
            raise DeploymentError("Vercel returned an invalid response")
        return body

    @staticmethod
    def _project_name(repository_name: str) -> str:
        normalized = re.sub(r"[^a-z0-9-]+", "-", repository_name.lower())
        normalized = re.sub(r"-+", "-", normalized).strip("-")
        if not normalized:
            raise DeploymentError("The repository name cannot be used as a Vercel project name")
        return normalized

    @staticmethod
    def _required_string(data: dict[str, Any], key: str) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value:
            raise DeploymentError(f"Vercel response is missing {key}")
        return value
