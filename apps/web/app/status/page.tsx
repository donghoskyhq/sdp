import { apiClient, type HealthResponse } from "@/lib/api-client";

export const dynamic = "force-dynamic";

interface HealthCheckResult {
  connected: boolean;
  data?: HealthResponse;
  message: string;
}

async function checkApi(): Promise<HealthCheckResult> {
  try {
    const data = await apiClient.health();
    return { connected: true, data, message: "FastAPI is reachable." };
  } catch {
    return {
      connected: false,
      message: "FastAPI is not reachable. Check API_BASE_URL and confirm the API service is running.",
    };
  }
}

export default async function StatusPage() {
  const result = await checkApi();

  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">Status</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Platform connectivity</h1>
      <section className="mt-10 rounded-2xl border border-white/10 bg-slate-900/70 p-8 shadow-2xl shadow-black/20">
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className={`h-3 w-3 rounded-full ${result.connected ? "bg-emerald-300" : "bg-rose-400"}`}
          />
          <h2 className="text-xl font-medium">Core API</h2>
        </div>
        <p className="mt-4 text-slate-300">{result.message}</p>
        {result.data ? (
          <dl className="mt-6 grid gap-4 text-sm sm:grid-cols-2">
            <div className="rounded-xl bg-white/[0.04] p-4">
              <dt className="text-slate-400">Service</dt>
              <dd className="mt-1 font-mono text-white">{result.data.service}</dd>
            </div>
            <div className="rounded-xl bg-white/[0.04] p-4">
              <dt className="text-slate-400">Version</dt>
              <dd className="mt-1 font-mono text-white">{result.data.version}</dd>
            </div>
          </dl>
        ) : null}
      </section>
    </main>
  );
}
