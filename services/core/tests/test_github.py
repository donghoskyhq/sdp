import json

import httpx

from shared.github import GitHubClient, load_nextjs_starter


def test_create_nextjs_repository_commits_starter() -> None:
    captured_tree: dict[str, object] = {}
    blob_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal blob_count
        path = request.url.path
        if request.method == "POST" and path == "/orgs/sky/repos":
            return httpx.Response(
                201,
                json={
                    "full_name": "sky/customer-portal",
                    "html_url": "https://github.com/sky/customer-portal",
                    "default_branch": "main",
                },
            )
        if request.method == "GET" and path.endswith("/git/ref/heads/main"):
            return httpx.Response(200, json={"object": {"sha": "initial-sha"}})
        if request.method == "POST" and path.endswith("/git/blobs"):
            blob_count += 1
            return httpx.Response(201, json={"sha": f"blob-{blob_count}"})
        if request.method == "POST" and path.endswith("/git/trees"):
            captured_tree.update(json.loads(request.content))
            return httpx.Response(201, json={"sha": "tree-sha"})
        if request.method == "POST" and path.endswith("/git/commits"):
            return httpx.Response(201, json={"sha": "commit-sha"})
        if request.method == "PATCH" and path.endswith("/git/ref/heads/main"):
            return httpx.Response(200, json={"object": {"sha": "commit-sha"}})
        return httpx.Response(500, json={"message": f"unexpected {request.method} {path}"})

    transport = httpx.MockTransport(handler)
    with httpx.Client(base_url="https://api.github.test", transport=transport) as http_client:
        client = GitHubClient(token="test", owner="sky", http_client=http_client)
        repository = client.create_nextjs_repository(
            name="customer-portal",
            project_name="Customer Portal",
            description=None,
            private=True,
        )

    assert repository.full_name == "sky/customer-portal"
    assert repository.default_branch == "main"
    tree = captured_tree["tree"]
    assert isinstance(tree, list)
    paths = {entry["path"] for entry in tree}
    assert {"package.json", "app/page.tsx", ".gitignore"}.issubset(paths)


def test_starter_replaces_project_markers() -> None:
    starter = load_nextjs_starter(
        project_name="Customer Portal", repository_name="customer-portal"
    )

    assert "Customer Portal" in starter["app/page.tsx"]
    assert '"name": "customer-portal"' in starter["package.json"]
    assert "__PROJECT_NAME__" not in "".join(starter.values())
