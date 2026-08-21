export type Platform = { id: "django" | "node" | "dotnet" | "docker"; label: string };
export type AppSummary = {
  ref: string;
  name: string;
  platform: Platform["id"];
  status: "running" | "stopped" | "degraded";
};
export type ServiceSummary = {
  ref: string;
  name: string;
  kind: "web" | "worker" | "cron";
  status: "healthy" | "degraded" | "stopped";
};


async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    credentials: "same-origin",
    ...init,
  });
  if (!response.ok) {
    throw new Error(`request_failed:${response.status}`);
  }
  return response.json() as Promise<T>;
}


export async function createSession(): Promise<void> {
  await requestJson("/sessions", { method: "POST" });
}


export async function listPlatforms(): Promise<Platform[]> {
  return (await requestJson<{ platforms: Platform[] }>("/fake-liara/platforms")).platforms;
}


export async function listApps(platform: Platform["id"]): Promise<AppSummary[]> {
  const query = new URLSearchParams({ platform });
  return (await requestJson<{ apps: AppSummary[] }>(`/fake-liara/apps?${query}`)).apps;
}


export async function listServices(appRef: string): Promise<ServiceSummary[]> {
  return (
    await requestJson<{ services: ServiceSummary[] }>(
      `/fake-liara/apps/${encodeURIComponent(appRef)}/services`,
    )
  ).services;
}
