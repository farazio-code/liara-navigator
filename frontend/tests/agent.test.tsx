import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";

import { App } from "../src/app/App";


afterEach(() => vi.restoreAllMocks());


it("submits a general topic and renders a validated citation", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
    const url = String(input);
    if (url.endsWith("/sessions")) {
      return Promise.resolve(new Response(JSON.stringify({ csrf_token: "x".repeat(32) }), { status: 201, headers: { "Content-Type": "application/json" } }));
    }
    if (url.endsWith("/turns/stream")) {
      const terminal = {
        status: "answer",
        message: "",
        model_calls: 1,
        claims: [{
          text: "رکورد DNS مناسب را ایجاد کنید.",
          role: "core",
          citation: {
            chunk_id: "dns-records",
            title: "مدیریت DNS",
            heading: "افزودن رکورد دامنه",
            url: "https://docs.liara.ir/dns/records",
            evidence: "رکورد DNS مناسب را در ناحیه دامنه ایجاد کنید",
          },
        }],
      };
      return Promise.resolve(new Response(`event: request.completed\ndata: ${JSON.stringify(terminal)}\n\n`, { status: 200, headers: { "Content-Type": "text/event-stream" } }));
    }
    throw new Error(`Unexpected request: ${url}`);
  });
  const user = userEvent.setup();
  render(<App />);

  await user.click(screen.getByRole("radio", { name: "DNS" }));
  await user.type(screen.getByRole("textbox", { name: "شرح مسئله" }), "دامنه من به برنامه متصل نمی‌شود");
  await user.click(screen.getByRole("button", { name: "شروع بررسی" }));

  expect(await screen.findByRole("heading", { name: "پاسخ مستند" })).toBeVisible();
  expect(screen.getByText("رکورد DNS مناسب را ایجاد کنید.")).toBeVisible();
  expect(screen.getAllByRole("link", { name: /مدیریت DNS/ })).toHaveLength(2);
});
