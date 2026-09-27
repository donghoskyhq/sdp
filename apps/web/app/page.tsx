import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-6xl items-center px-6 py-20">
      <section className="max-w-3xl">
        <p className="mb-5 text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">
          Internal developer platform
        </p>
        <h1 className="text-5xl font-semibold tracking-tight text-white sm:text-7xl">
          Sky Dev Platform
        </h1>
        <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-300">
          A self-service foundation for Sky teams to create, run, and evolve software projects.
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <Link
            className="rounded-full bg-emerald-300 px-6 py-3 font-semibold text-slate-950 transition hover:bg-emerald-200"
            href="/dashboard"
          >
            Open dashboard
          </Link>
          <Link
            className="rounded-full border border-white/20 px-6 py-3 font-semibold text-white transition hover:border-white/40 hover:bg-white/5"
            href="/status"
          >
            Check platform status
          </Link>
        </div>
      </section>
    </main>
  );
}
