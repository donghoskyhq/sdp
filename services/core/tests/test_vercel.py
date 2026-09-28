import json

import httpx

from shared.vercel import VercelClient


def test_deploy_github_repository_creates_project_and_waits_until_ready() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST" and request.url.path == "/v11/projects":
            return httpx.Response(201, json={"id": "prj_123"})
        if request.method == "POST" and request.url.path == "/v13/deployments":
            return httpx.Response(
                200,
                json={
                    "id": "dpl_123",
                    "readyState": "BUILDING",
                    "url": "example.vercel.app",
                },
            )
        if request.method == "GET" and request.url.path == "/v13/deployments/dpl_123":
            return httpx.Response(
                200,
                json={
                    "id": "dpl_123",
                    "readyState": "READY",
                    "url": "example.vercel.app",
                },
            )
        return httpx.Response(500, json={"error": {"message": "unexpected request"}})

    with httpx.Client(
        base_url="https://api.vercel.test", transport=httpx.MockTransport(handler)
    ) as http_client:
        client = VercelClient(
            token="test",
            team_id="team_123",
            poll_interval_seconds=0,
            http_client=http_client,
        )
        result = client.deploy_github_repository(
            repository_full_name="sky/example_project",
            repository_name="example_project",
            branch="main",
        )

    assert result.project_id == "prj_123"
    assert result.deployment_id == "dpl_123"
    assert result.deployment_url == "https://example.vercel.app"
    assert all(request.url.params["teamId"] == "team_123" for request in requests)

    project_body = json.loads(requests[0].content)
    assert project_body == {
        "name": "example-project",
        "framework": "nextjs",
        "gitRepository": {"type": "github", "repo": "sky/example_project"},
    }
    deployment_body = json.loads(requests[1].content)
    assert deployment_body["project"] == "prj_123"
    assert deployment_body["target"] == "production"
    assert deployment_body["gitSource"] == {
        "type": "github",
        "repo": "sky/example_project",
        "ref": "main",
    }
