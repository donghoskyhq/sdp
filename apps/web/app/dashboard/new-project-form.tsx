"use client";

import { useActionState, useEffect, useRef } from "react";
import { useFormStatus } from "react-dom";

import { createProjectAction, type CreateProjectState } from "./actions";

const initialState: CreateProjectState = { status: "idle", message: "" };

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      className="rounded-full bg-emerald-300 px-6 py-3 font-semibold text-slate-950 transition hover:bg-emerald-200 disabled:cursor-wait disabled:opacity-60"
      disabled={pending}
      type="submit"
    >
      {pending ? "Starting project…" : "Start project"}
    </button>
  );
}

export function NewProjectForm() {
  const [state, formAction] = useActionState(createProjectAction, initialState);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (state.status === "success") formRef.current?.reset();
  }, [state.status]);

  return (
    <form action={formAction} className="grid gap-5" ref={formRef}>
      <div className="grid gap-5 sm:grid-cols-2">
        <label className="grid gap-2 text-sm font-medium">
          Project name
          <input
            className="rounded-xl border border-white/15 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-emerald-300"
            maxLength={100}
            name="name"
            placeholder="Customer portal"
            required
          />
        </label>
        <label className="grid gap-2 text-sm font-medium">
          GitHub repository
          <input
            className="rounded-xl border border-white/15 bg-slate-950/60 px-4 py-3 font-mono text-white outline-none transition placeholder:text-slate-600 focus:border-emerald-300"
            maxLength={100}
            name="repositoryName"
            pattern="[a-z0-9][a-z0-9._-]*"
            placeholder="customer-portal"
            required
          />
        </label>
      </div>
      <label className="grid gap-2 text-sm font-medium">
        Description <span className="font-normal text-slate-500">Optional</span>
        <textarea
          className="min-h-24 resize-y rounded-xl border border-white/15 bg-slate-950/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-emerald-300"
          maxLength={350}
          name="description"
          placeholder="What will this project help the team deliver?"
        />
      </label>
      <fieldset className="grid gap-3">
        <legend className="text-sm font-medium">Deployment target</legend>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="cursor-pointer rounded-xl border border-white/15 bg-slate-950/60 p-4 transition has-[:checked]:border-emerald-300 has-[:checked]:bg-emerald-300/5">
            <span className="flex items-center gap-3">
              <input
                className="size-4 accent-emerald-300"
                defaultChecked
                name="deploymentTarget"
                type="radio"
                value="vercel"
              />
              <span className="font-semibold">Vercel</span>
            </span>
            <span className="mt-2 block pl-7 text-sm font-normal text-slate-400">
              Deploy the Next.js application as a production deployment.
            </span>
          </label>
          <label className="cursor-pointer rounded-xl border border-white/15 bg-slate-950/60 p-4 transition has-[:checked]:border-emerald-300 has-[:checked]:bg-emerald-300/5">
            <span className="flex items-center gap-3">
              <input
                className="size-4 accent-emerald-300"
                name="deploymentTarget"
                type="radio"
                value="railway"
              />
              <span className="font-semibold">Railway</span>
            </span>
            <span className="mt-2 block pl-7 text-sm font-normal text-slate-400">
              Create a Railway project, service, public domain, and deployment.
            </span>
          </label>
        </div>
      </fieldset>
      <div className="flex flex-wrap items-center gap-4">
        <SubmitButton />
        {state.message ? (
          <p
            aria-live="polite"
            className={state.status === "error" ? "text-sm text-rose-300" : "text-sm text-emerald-300"}
          >
            {state.message}
          </p>
        ) : null}
      </div>
    </form>
  );
}
