import json

import httpx

from shared.railway import RailwayClient


def test_deploy_github_repository_creates_railway_resources() -> None:
    variables_by_operation: dict[str, dict[str, object]] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        query = body["query"]
        variables = body["variables"]
        if "mutation projectCreate" in query:
            variables_by_operation["projectCreate"] = variables
            return httpx.Response(
                200, json={"data": {"projectCreate": {"id": "prj_123", "name": "Example"}}}
            )
        if "query project" in query:
            return httpx.Response(
                200,
                json={
                    "data": {
                        "project": {
                            "environments": {
                                "edges": [
                                    {"node": {"id": "env_123", "name": "production"}}
                                ]
                            }
                        }
                    }
                },
            )
        if "mutation serviceCreate" in query:
            variables_by_operation["serviceCreate"] = variables
            return httpx.Response(
                200, json={"data": {"serviceCreate": {"id": "svc_123", "name": "example"}}}
            )
        if "mutation serviceDomainCreate" in query:
            return httpx.Response(
                200,
                json={
                    "data": {
                        "serviceDomainCreate": {
                            "id": "domain_123",
                            "domain": "example.up.railway.app",
                        }
                    }
                },
            )
        if "mutation serviceInstanceDeployV2" in query:
            return httpx.Response(
                200, json={"data": {"serviceInstanceDeployV2": "dpl_123"}}
            )
        if "query deployment" in query:
            return httpx.Response(
                200,
                json={"data": {"deployment": {"id": "dpl_123", "status": "SUCCESS"}}},
            )
        return httpx.Response(500)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = RailwayClient(
            token="test",
            workspace_id="workspace_123",
            api_url="https://backboard.railway.test/graphql/v2",
            poll_interval_seconds=0,
            http_client=http_client,
        )
        result = client.deploy_github_repository(
            repository_full_name="sky/example",
            repository_name="example",
            project_name="Example",
            description="An example",
            branch="main",
        )

    assert result.project_id == "prj_123"
    assert result.service_id == "svc_123"
    assert result.deployment_id == "dpl_123"
    assert result.deployment_url == "https://example.up.railway.app"
    assert variables_by_operation["projectCreate"] == {
        "input": {
            "name": "Example",
            "description": "An example",
            "workspaceId": "workspace_123",
        }
    }
    assert variables_by_operation["serviceCreate"] == {
        "input": {
            "projectId": "prj_123",
            "name": "example",
            "branch": "main",
            "source": {"repo": "sky/example"},
        }
    }
