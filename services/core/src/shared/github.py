from dataclasses import dataclass
from typing import Any, Literal

import httpx

from shared.config import Settings


class GitHubError(RuntimeError):
    """A safe-to-log error returned by the GitHub API integration."""


@dataclass(frozen=True)
class GitHubRepository:
    full_name: str
    html_url: str
    default_branch: str


class GitHubClient:
    def __init__(
        self,
        *,
        token: str,
        owner: str,
        owner_type: Literal["organization", "user"] = "organization",
        api_url: str = "https://api.github.com",
        http_client: httpx.Client | None = None,
    ) -> None:
        if not token or not owner:
            raise GitHubError("GitHub provisioning is not configured")

        self.owner = owner
        self.owner_type = owner_type
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=api_url.rstrip("/"),
            timeout=30.0,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "sky-dev-platform",
            },
        )

    @classmethod
    def from_settings(cls, settings: Settings) -> "GitHubClient":
        return cls(
            token=settings.github_token,
            owner=settings.github_owner,
            owner_type=settings.github_owner_type,
            api_url=settings.github_api_url,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "GitHubClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def create_nextjs_repository(
        self,
        *,
        name: str,
        project_name: str,
        description: str | None,
        private: bool,
    ) -> GitHubRepository:
        endpoint = f"/orgs/{self.owner}/repos"
        if self.owner_type == "user":
            endpoint = "/user/repos"

        repository = self._request(
            "POST",
            endpoint,
            expected_status=201,
            json={
                "name": name,
                "description": description or f"{project_name} — created by Sky Dev Platform",
                "private": private,
                "auto_init": True,
            },
        )
        full_name = self._required_string(repository, "full_name")
        html_url = self._required_string(repository, "html_url")
        default_branch = repository.get("default_branch", "main")
        if not isinstance(default_branch, str):
            raise GitHubError("GitHub returned an invalid default branch")

        self._replace_initial_content(
            full_name=full_name,
            default_branch=default_branch,
            files=load_nextjs_starter(project_name=project_name, repository_name=name),
        )
        return GitHubRepository(
            full_name=full_name,
            html_url=html_url,
            default_branch=default_branch,
        )

    def _replace_initial_content(
        self, *, full_name: str, default_branch: str, files: dict[str, str]
    ) -> None:
        ref_path = f"/repos/{full_name}/git/ref/heads/{default_branch}"
        ref = self._request("GET", ref_path, expected_status=200)
        ref_object = ref.get("object")
        if not isinstance(ref_object, dict) or not isinstance(ref_object.get("sha"), str):
            raise GitHubError("GitHub returned an invalid branch reference")
        parent_sha = ref_object["sha"]

        tree_entries: list[dict[str, str]] = []
        for path, content in files.items():
            blob = self._request(
                "POST",
                f"/repos/{full_name}/git/blobs",
                expected_status=201,
                json={"content": content, "encoding": "utf-8"},
            )
            tree_entries.append(
                {
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": self._required_string(blob, "sha"),
                }
            )

        tree = self._request(
            "POST",
            f"/repos/{full_name}/git/trees",
            expected_status=201,
            json={"tree": tree_entries},
        )
        commit = self._request(
            "POST",
            f"/repos/{full_name}/git/commits",
            expected_status=201,
            json={
                "message": "Initialize Next.js project",
                "tree": self._required_string(tree, "sha"),
                "parents": [parent_sha],
            },
        )
        self._request(
            "PATCH",
            ref_path,
            expected_status=200,
            json={"sha": self._required_string(commit, "sha"), "force": False},
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = self._client.request(method, path, json=json)
        except httpx.HTTPError as exc:
            raise GitHubError("GitHub could not be reached") from exc

        if response.status_code != expected_status:
            request_id = response.headers.get("x-github-request-id", "unknown")
            message = "request failed"
            try:
                body = response.json()
                if isinstance(body, dict) and isinstance(body.get("message"), str):
                    message = body["message"]
            except ValueError:
                pass
            raise GitHubError(
                f"GitHub API returned {response.status_code}: {message} (request {request_id})"
            )

        body = response.json()
        if not isinstance(body, dict):
            raise GitHubError("GitHub returned an invalid response")
        return body

    @staticmethod
    def _required_string(data: dict[str, Any], key: str) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value:
            raise GitHubError(f"GitHub response is missing {key}")
        return value


def load_nextjs_starter(*, project_name: str, repository_name: str) -> dict[str, str]:
    from importlib.resources import files

    root = files("worker.templates.nextjs")
    result: dict[str, str] = {}
    for resource in root.iterdir():
        if resource.name == "__init__.py":
            continue
        if resource.is_dir() and resource.name in {"app", "public"}:
            for child in resource.iterdir():
                if child.is_file() and not child.name.startswith("__"):
                    result[f"{resource.name}/{child.name}"] = child.read_text(encoding="utf-8")
        elif resource.is_file() and not resource.name.startswith("__"):
            result[resource.name] = resource.read_text(encoding="utf-8")

    result[".gitignore"] = result.pop("gitignore.template")
    result["public/.gitkeep"] = result.pop("public/gitkeep.template")

    replacements = {
        "__PROJECT_NAME__": project_name,
        "__REPOSITORY_NAME__": repository_name,
    }
    for path, content in result.items():
        for marker, value in replacements.items():
            content = content.replace(marker, value)
        result[path] = content
    return result
