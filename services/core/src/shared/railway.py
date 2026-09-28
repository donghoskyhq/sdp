import time
from typing import Any

import httpx

from shared.config import Settings
from shared.deployments import DeploymentError, DeploymentResult


class RailwayClient:
    def __init__(
        self,
        *,
        token: str,
        workspace_id: str = "",
        api_url: str = "https://backboard.railway.com/graphql/v2",
        poll_interval_seconds: float = 5.0,
        timeout_seconds: int = 900,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not token:
            raise DeploymentError("Railway provisioning is not configured")

        self.workspace_id = workspace_id
        self.poll_interval_seconds = poll_interval_seconds
        self.timeout_seconds = timeout_seconds
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "sky-dev-platform",
            },
        )
        self._api_url = api_url

    @classmethod
    def from_settings(cls, settings: Settings) -> "RailwayClient":
        return cls(
            token=settings.railway_token,
            workspace_id=settings.railway_workspace_id,
            api_url=settings.railway_api_url,
            poll_interval_seconds=settings.deployment_poll_interval_seconds,
            timeout_seconds=settings.deployment_timeout_seconds,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "RailwayClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def deploy_github_repository(
        self,
        *,
        repository_full_name: str,
        repository_name: str,
        project_name: str,
        description: str | None,
        branch: str,
    ) -> DeploymentResult:
        project_input: dict[str, Any] = {"name": project_name}
        if description:
            project_input["description"] = description
        if self.workspace_id:
            project_input["workspaceId"] = self.workspace_id

        project_data = self._graphql(
            """
            mutation projectCreate($input: ProjectCreateInput!) {
              projectCreate(input: $input) { id name }
            }
            """,
            {"input": project_input},
        )
        project = self._required_object(project_data, "projectCreate")
        project_id = self._required_string(project, "id")
        environment_id = self._production_environment_id(project_id)

        service_data = self._graphql(
            """
            mutation serviceCreate($input: ServiceCreateInput!) {
              serviceCreate(input: $input) { id name }
            }
            """,
            {
                "input": {
                    "projectId": project_id,
                    "name": repository_name,
                    "branch": branch,
                    "source": {"repo": repository_full_name},
                }
            },
        )
        service = self._required_object(service_data, "serviceCreate")
        service_id = self._required_string(service, "id")

        domain_data = self._graphql(
            """
            mutation serviceDomainCreate($input: ServiceDomainCreateInput!) {
              serviceDomainCreate(input: $input) { id domain }
            }
            """,
            {"input": {"serviceId": service_id, "environmentId": environment_id}},
        )
        domain = self._required_object(domain_data, "serviceDomainCreate")
        domain_name = self._required_string(domain, "domain")

        deploy_data = self._graphql(
            """
            mutation serviceInstanceDeployV2($serviceId: String!, $environmentId: String!) {
              serviceInstanceDeployV2(serviceId: $serviceId, environmentId: $environmentId)
            }
            """,
            {"serviceId": service_id, "environmentId": environment_id},
        )
        deployment_id = self._required_string(deploy_data, "serviceInstanceDeployV2")
        self._wait_for_deployment(deployment_id)

        return DeploymentResult(
            project_id=project_id,
            service_id=service_id,
            deployment_id=deployment_id,
            deployment_url=f"https://{domain_name}",
            project_url=f"https://railway.com/project/{project_id}",
        )

    def _production_environment_id(self, project_id: str) -> str:
        data = self._graphql(
            """
            query project($id: String!) {
              project(id: $id) {
                environments { edges { node { id name } } }
              }
            }
            """,
            {"id": project_id},
        )
        project = self._required_object(data, "project")
        environments = self._required_object(project, "environments")
        edges = environments.get("edges")
        if not isinstance(edges, list) or not edges:
            raise DeploymentError("Railway project has no environment")
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            node = edge.get("node")
            if isinstance(node, dict) and node.get("name") == "production":
                return self._required_string(node, "id")
        first = edges[0]
        if not isinstance(first, dict):
            raise DeploymentError("Railway returned an invalid environment")
        return self._required_string(self._required_object(first, "node"), "id")

    def _wait_for_deployment(self, deployment_id: str) -> None:
        deadline = time.monotonic() + self.timeout_seconds
        while True:
            data = self._graphql(
                """
                query deployment($id: String!) {
                  deployment(id: $id) { id status }
                }
                """,
                {"id": deployment_id},
            )
            deployment = self._required_object(data, "deployment")
            status = self._required_string(deployment, "status")
            if status == "SUCCESS":
                return
            if status in {"FAILED", "CRASHED", "REMOVED", "SKIPPED"}:
                raise DeploymentError(f"Railway deployment failed: {status}")
            if time.monotonic() >= deadline:
                raise DeploymentError("Railway deployment timed out")
            time.sleep(self.poll_interval_seconds)

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.post(
                self._api_url,
                json={"query": query, "variables": variables},
            )
        except httpx.HTTPError as exc:
            raise DeploymentError("Railway could not be reached") from exc

        if response.status_code != 200:
            raise DeploymentError(f"Railway API returned {response.status_code}")
        body = response.json()
        if not isinstance(body, dict):
            raise DeploymentError("Railway returned an invalid response")
        errors = body.get("errors")
        if isinstance(errors, list) and errors:
            first = errors[0]
            message = first.get("message") if isinstance(first, dict) else None
            detail = message if isinstance(message, str) and message else "request failed"
            raise DeploymentError(f"Railway API error: {detail}")
        data = body.get("data")
        if not isinstance(data, dict):
            raise DeploymentError("Railway response is missing data")
        return data

    @staticmethod
    def _required_object(data: dict[str, Any], key: str) -> dict[str, Any]:
        value = data.get(key)
        if not isinstance(value, dict):
            raise DeploymentError(f"Railway response is missing {key}")
        return value

    @staticmethod
    def _required_string(data: dict[str, Any], key: str) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value:
            raise DeploymentError(f"Railway response is missing {key}")
        return value
