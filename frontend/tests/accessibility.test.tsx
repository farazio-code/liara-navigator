import { render } from "@testing-library/react";
import axe from "axe-core";
import { afterEach, expect, it, vi } from "vitest";

import { App } from "../src/app/App";


afterEach(() => vi.restoreAllMocks());


it("has no serious accessibility violations in the initial RTL workspace", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ csrf_token: "x".repeat(32) }), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    }),
  );
  const { container } = render(<App />);

  const result = await axe.run(container, {
    rules: { "color-contrast": { enabled: false } },
  });
  const serious = result.violations.filter(
    (violation) => violation.impact === "serious" || violation.impact === "critical",
  );

  expect(serious).toEqual([]);
});
