export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">Dashboard</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Projects</h1>
      <section className="mt-10 rounded-2xl border border-dashed border-white/20 bg-white/[0.03] p-10">
        <h2 className="text-xl font-medium">Project provisioning is coming next.</h2>
        <p className="mt-3 max-w-2xl leading-7 text-slate-400">
          This initial dashboard is a placeholder. GitHub, Harness, and deployment-provider workflows
          are intentionally not connected yet.
        </p>
      </section>
    </main>
  );
}
