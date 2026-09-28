"use server";

import { revalidatePath } from "next/cache";

import { ApiClientError, apiClient, type DeploymentTarget } from "@/lib/api-client";

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
  const deploymentTarget = String(formData.get("deploymentTarget") ?? "");

  if (!name || !repositoryName) {
    return { status: "error", message: "Project name and repository name are required." };
  }

  if (!/^[a-z0-9][a-z0-9._-]*$/.test(repositoryName)) {
    return {
      status: "error",
      message: "Use lowercase letters, numbers, dots, underscores, and hyphens; start with a letter or number.",
    };
  }

  if (deploymentTarget !== "vercel" && deploymentTarget !== "railway") {
    return { status: "error", message: "Choose Vercel or Railway as the deployment target." };
  }

  try {
    await apiClient.createProject({
      name,
      repository_name: repositoryName,
      deployment_target: deploymentTarget as DeploymentTarget,
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
