import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "../src/app/App";
import "../src/styles/tokens.css";


describe("application shell", () => {
  it("renders the Persian RTL workspace landmarks", () => {
    const { container } = render(<App />);

    const shell = container.firstElementChild;
    expect(shell).toHaveAttribute("dir", "rtl");
    expect(shell).toHaveAttribute("lang", "fa");
    expect(screen.getByRole("navigation", { name: "ناوبری اصلی" })).toBeInTheDocument();
    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(screen.getByRole("complementary", { name: "منابع پاسخ" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "مسئله را انتخاب کن؛ با شواهد حلش می‌کنیم." })).toBeInTheDocument();
  });

  it("loads the canonical dark Liara design tokens", () => {
    document.documentElement.dataset.theme = "dark";
    render(<App />);

    const styles = getComputedStyle(document.documentElement);
    expect(styles.getPropertyValue("--lids-brand-mint").trim()).toBe("#87fcc4");
    expect(styles.getPropertyValue("--lids-brand-cyan").trim()).toBe("#28c1f5");
    expect(styles.getPropertyValue("--lids-bg-canvas").trim()).toBe("#181818");
    expect(styles.getPropertyValue("--lids-radius-card").trim()).toBe("12px");
  });
});
