import { apiClient, type Project, type ProjectStatus } from "@/lib/api-client";

import { NewProjectForm } from "./new-project-form";
import { ProjectRefresh } from "./project-refresh";

export const dynamic = "force-dynamic";

const statusStyles: Record<ProjectStatus, string> = {
  pending: "bg-amber-300/10 text-amber-200",
  provisioning: "bg-sky-300/10 text-sky-200",
  ready: "bg-emerald-300/10 text-emerald-200",
  failed: "bg-rose-300/10 text-rose-200",
};

async function loadProjects(): Promise<{ projects: Project[]; unavailable: boolean }> {
  try {
    return { projects: await apiClient.projects(), unavailable: false };
  } catch {
    return { projects: [], unavailable: true };
  }
}

export default async function DashboardPage() {
  const { projects, unavailable } = await loadProjects();
  const hasActiveProjects = projects.some(
    (project) => project.status === "pending" || project.status === "provisioning",
  );

  return (
    <main className="mx-auto max-w-6xl px-6 py-16">
      <ProjectRefresh enabled={hasActiveProjects} />
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">Dashboard</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Projects</h1>
      <p className="mt-3 text-slate-400">
        Start with a private GitHub repository and deploy a ready-to-run Next.js application.
      </p>

      <section className="mt-10 rounded-2xl border border-white/10 bg-white/[0.03] p-6 sm:p-8">
        <h2 className="text-xl font-medium">Start a new project</h2>
        <p className="mb-6 mt-2 text-sm leading-6 text-slate-400">
          The platform creates the repository, commits the default TypeScript App Router starter,
          and deploys it to Vercel or Railway.
        </p>
        <NewProjectForm />
      </section>

      <section className="mt-12">
        <h2 className="text-xl font-medium">Recent projects</h2>
        {unavailable ? (
          <p className="mt-4 rounded-xl border border-rose-300/20 bg-rose-300/5 p-4 text-rose-200">
            Projects could not be loaded. Check the Core API and database connection.
          </p>
        ) : projects.length === 0 ? (
          <p className="mt-4 rounded-xl border border-dashed border-white/20 p-8 text-slate-400">
            No projects yet. Create the first one above.
          </p>
        ) : (
          <div className="mt-4 grid gap-4">
            {projects.map((project) => (
              <article className="rounded-2xl border border-white/10 bg-slate-900/60 p-5" key={project.id}>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-lg font-semibold">{project.name}</h3>
                      {project.deployment_target ? (
                        <span className="rounded-full border border-white/10 px-2 py-0.5 text-xs font-medium capitalize text-slate-300">
                          {project.deployment_target}
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-1 font-mono text-sm text-slate-400">
                      {project.github_full_name ?? project.repository_name}
                    </p>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wider ${statusStyles[project.status]}`}
                  >
                    {project.status}
                  </span>
                </div>
                {project.description ? <p className="mt-4 text-sm text-slate-300">{project.description}</p> : null}
                {project.status === "ready" ? (
                  <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-sm font-semibold">
                    {project.deployment_url ? (
                      <a
                        className="text-emerald-300 hover:text-emerald-200"
                        href={project.deployment_url}
                        rel="noreferrer"
                        target="_blank"
                      >
                        Open deployment ↗
                      </a>
                    ) : null}
                    {project.github_url ? (
                      <a
                        className="text-slate-300 hover:text-white"
                        href={project.github_url}
                        rel="noreferrer"
                        target="_blank"
                      >
                        GitHub ↗
                      </a>
                    ) : null}
                    {project.deployment_project_url ? (
                      <a
                        className="text-slate-300 hover:text-white"
                        href={project.deployment_project_url}
                        rel="noreferrer"
                        target="_blank"
                      >
                        Provider dashboard ↗
                      </a>
                    ) : null}
                  </div>
                ) : null}
                {project.status === "failed" && project.error_message ? (
                  <p className="mt-4 text-sm text-rose-300">{project.error_message}</p>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
