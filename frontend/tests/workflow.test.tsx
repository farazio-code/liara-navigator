import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/app/App";


const jsonResponse = (body: unknown, status = 200) =>
  Promise.resolve(new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  }));


afterEach(() => vi.restoreAllMocks());


describe("support and agentic workflow", () => {
  it("switches between the support ticket and agentic paths", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(() => jsonResponse({
      session: {
        status: "active",
        connection_state: "anonymous",
        idle_expires_at: "2026-08-21T20:00:00Z",
        absolute_expires_at: "2026-08-21T22:00:00Z",
      },
      csrf_token: "x".repeat(32),
    }, 201));
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByRole("tab", { name: "دستیار هوشمند" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    await user.click(screen.getByRole("tab", { name: "تیکت پشتیبانی" }));
    expect(screen.getByRole("heading", { name: "ارسال تیکت برای تیم پشتیبانی" })).toBeVisible();
  });

  it("loads dependent PaaS app and service choices", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.endsWith("/sessions")) {
        return jsonResponse({
          session: {
            status: "active",
            connection_state: "anonymous",
            idle_expires_at: "2026-08-21T20:00:00Z",
            absolute_expires_at: "2026-08-21T22:00:00Z",
          },
          csrf_token: "x".repeat(32),
        }, 201);
      }
      if (url.endsWith("/platforms")) {
        return jsonResponse({ platforms: [{ id: "django", label: "Python / Django" }] });
      }
      if (url.includes("/apps?platform=django")) {
        return jsonResponse({
          apps: [{ ref: "opaque-app", name: "فروشگاه", platform: "django", status: "running" }],
        });
      }
      if (url.endsWith("/apps/opaque-app/services")) {
        return jsonResponse({
          services: [{ ref: "opaque-service", name: "web", kind: "web", status: "healthy" }],
        });
      }
      throw new Error(`Unexpected request: ${url}`);
    });
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("radio", { name: "PaaS" }));
    const platform = await screen.findByRole("combobox", { name: "نوع پلتفرم" });
    await user.selectOptions(platform, "django");
    await user.click(await screen.findByRole("button", { name: /فروشگاه/ }));
    await user.click(await screen.findByRole("button", { name: /web/ }));

    expect(screen.getByText("سرویس انتخاب‌شده: web")).toBeVisible();
    expect(screen.getByText(/حداکثر ۱۰۰ خط آخر لاگ/)).toBeVisible();
    expect(screen.getByRole("textbox", { name: "شرح مسئله" })).toBeEnabled();
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(4));
  });
});
