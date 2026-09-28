export interface HealthResponse {
  status: "ok";
  service: string;
  version: string;
}

export interface ApiStatusResponse {
  status: "ok";
  service: string;
  version: string;
  environment: string;
  database: "configured" | "not_configured";
  redis: "configured" | "not_configured";
}

export type ProjectStatus = "pending" | "provisioning" | "ready" | "failed";

export interface Project {
  id: string;
  name: string;
  repository_name: string;
  description: string | null;
  status: ProjectStatus;
  github_url: string | null;
  github_full_name: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateInput {
  name: string;
  repository_name: string;
  description?: string;
}

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

const apiBaseUrl = (): string => process.env.API_BASE_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new ApiClientError(`API request failed with status ${response.status}`, response.status);
  }

  return (await response.json()) as T;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    method: "POST",
    cache: "no-store",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let message = `API request failed with status ${response.status}`;
    try {
      const data = (await response.json()) as { detail?: string };
      if (data.detail) message = data.detail;
    } catch {
      // Keep the status-based fallback when the response is not JSON.
    }
    throw new ApiClientError(message, response.status);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  health: (): Promise<HealthResponse> => get<HealthResponse>("/health"),
  status: (): Promise<ApiStatusResponse> => get<ApiStatusResponse>("/api/v1/status"),
  projects: (): Promise<Project[]> => get<Project[]>("/api/v1/projects"),
  createProject: (input: ProjectCreateInput): Promise<Project> =>
    post<Project>("/api/v1/projects", input),
};
