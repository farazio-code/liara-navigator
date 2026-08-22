import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";

import { App } from "../src/app/App";


afterEach(() => vi.restoreAllMocks());


it("submits the bounded mock support ticket and explains that it is not real", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
    const url = String(input);
    if (url.endsWith("/sessions")) {
      return Promise.resolve(new Response(JSON.stringify({ csrf_token: "x".repeat(32) }), { status: 201, headers: { "Content-Type": "application/json" } }));
    }
    if (url.endsWith("/tickets")) {
      return Promise.resolve(new Response(JSON.stringify({ ticket_ref: "tkt_demo123", status: "accepted_mock" }), { status: 201, headers: { "Content-Type": "application/json" } }));
    }
    throw new Error(`Unexpected request: ${url}`);
  });
  const user = userEvent.setup();
  render(<App />);

  await user.click(screen.getByRole("tab", { name: "تیکت پشتیبانی" }));
  await user.type(screen.getByRole("textbox", { name: "عنوان تیکت" }), "دامنه به برنامه وصل نمی‌شود");
  await user.type(screen.getByRole("textbox", { name: "شرح مسئله" }), "رکورد را تنظیم کرده‌ام اما هنوز پاسخ برنامه دیده نمی‌شود.");
  await user.click(screen.getByRole("button", { name: "ثبت تیکت آزمایشی" }));

  expect(await screen.findByText("تیکت آزمایشی ثبت شد.")).toBeVisible();
  expect(screen.getByText(/به سامانه واقعی پشتیبانی ارسال نشده/)).toBeVisible();
});
