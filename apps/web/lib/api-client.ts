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

export const apiClient = {
  health: (): Promise<HealthResponse> => get<HealthResponse>("/health"),
  status: (): Promise<ApiStatusResponse> => get<ApiStatusResponse>("/api/v1/status"),
};
