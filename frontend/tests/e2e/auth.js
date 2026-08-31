// The dev superuser from .env.dev. Read from the environment rather than
// hard-coded so this file carries no password, and so CI can point at its own.
import { expect } from "@playwright/test";

export const USERNAME = process.env.E2E_USERNAME ?? "jadams";
export const PASSWORD = process.env.E2E_PASSWORD;

export async function login(page) {
  if (!PASSWORD) {
    throw new Error(
      "E2E_PASSWORD is not set. Export it from .env.dev " +
        "(DJANGO_SUPERUSER_PASSWORD) before running the e2e suite.",
    );
  }
  await page.goto("/login");
  // Exact, because the show/hide toggle's accessible name also contains
  // "Password" and a substring match is a strict-mode violation.
  await page.getByLabel("Username", { exact: true }).fill(USERNAME);
  await page.getByLabel("Password", { exact: true }).fill(PASSWORD);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).not.toHaveURL(/\/login/);
}

/**
 * Reach the savings plan the way a person does.
 *
 * `page.goto("/planning/savings-plan")` cannot work: the router guard sends
 * any full page load of a non-root route back to the dashboard, so a deep link
 * silently lands on "/" and the assertions then fail somewhere confusing. The
 * left rail swaps the second drawer between accounts and planning; the folder
 * icon is what selects planning.
 */
export async function openSavingsPlan(page) {
  await page.locator(".mdi-folder").first().click();
  await page.getByRole("link", { name: "Savings Plan" }).click();
  await expect(page).toHaveURL(/\/planning\/savings-plan/);
  // The plan projects a year across every account, which takes seconds.
  await expect(page.getByText("Allocates per paycheck")).toBeVisible({
    timeout: 60_000,
  });
}
