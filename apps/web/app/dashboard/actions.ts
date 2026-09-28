"use server";

import { revalidatePath } from "next/cache";

import { ApiClientError, apiClient } from "@/lib/api-client";

export interface CreateProjectState {
  status: "idle" | "success" | "error";
  message: string;
}

export async function createProjectAction(
  _previousState: CreateProjectState,
  formData: FormData,
): Promise<CreateProjectState> {
  const name = String(formData.get("name") ?? "").trim();
  const repositoryName = String(formData.get("repositoryName") ?? "").trim();
  const description = String(formData.get("description") ?? "").trim();

  if (!name || !repositoryName) {
    return { status: "error", message: "Project name and repository name are required." };
  }

  if (!/^[a-z0-9][a-z0-9._-]*$/.test(repositoryName)) {
    return {
      status: "error",
      message: "Use lowercase letters, numbers, dots, underscores, and hyphens; start with a letter or number.",
    };
  }

  try {
    await apiClient.createProject({
      name,
      repository_name: repositoryName,
      ...(description ? { description } : {}),
    });
    revalidatePath("/dashboard");
    return { status: "success", message: "Provisioning started. This page will update shortly." };
  } catch (error) {
    const message =
      error instanceof ApiClientError ? error.message : "The project could not be created.";
    return { status: "error", message };
  }
}
