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
  await page.getByLabel("Username").fill(USERNAME);
  await page.getByLabel("Password").fill(PASSWORD);
  await page.getByRole("button", { name: /sign in|log in|login/i }).click();
  await expect(page).not.toHaveURL(/\/login/);
}
