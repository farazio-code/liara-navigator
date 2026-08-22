import { parseTerminalEvent, type TerminalResult } from "./events";

export type PlatformId =
  | "angular"
  | "django"
  | "docker"
  | "dotnet"
  | "flask"
  | "go"
  | "laravel"
  | "nextjs"
  | "nodejs"
  | "php"
  | "python"
  | "react"
  | "static"
  | "vue";
export type Platform = { id: PlatformId; label: string };
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


export async function createSession(): Promise<string> {
  const response = await requestJson<{ csrf_token: string }>("/sessions", { method: "POST" });
  return response.csrf_token;
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


export async function submitTurn(
  topic: "paas" | "cdn" | "ssl" | "dns" | "other",
  message: string,
  csrfToken: string,
  serviceRef?: string,
): Promise<TerminalResult> {
  const response = await fetch("/api/v1/turns/stream", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    body: JSON.stringify({
      client_request_id: `turn-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
      topic,
      message,
      service_ref: serviceRef,
    }),
  });
  if (!response.ok) throw new Error(`request_failed:${response.status}`);
  return parseTerminalEvent(await response.text());
}


export async function submitTicket(input: {
  topic: "paas" | "cdn" | "ssl" | "dns" | "other";
  subject: string;
  description: string;
  handoffSummary?: string;
}, csrfToken: string): Promise<{ ticket_ref: string; status: "accepted_mock" }> {
  return requestJson("/tickets", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    body: JSON.stringify({
      topic: input.topic,
      subject: input.subject,
      description: input.description,
      handoff_summary: input.handoffSummary,
    }),
  });
}
