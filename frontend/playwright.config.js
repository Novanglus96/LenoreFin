// Playwright drives the dev server that is already running in Docker
// (`docker compose up`), rather than starting one: the frontend proxies to
// back-dev.danielleandjohn.love, which needs the compose network and the
// backend container behind it. Starting a second Vite here would talk to the
// same backend anyway and race the first for port 8081.
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  // These drive one shared backend holding real data, so they must not run
  // against each other: two workers adding and deleting buckets at once would
  // fail on each other's rows rather than on a bug.
  workers: 1,
  fullyParallel: false,
  // A savings plan projects a year across eleven accounts and takes seconds.
  timeout: 60_000,
  expect: { timeout: 15_000 },
  reporter: process.env.CI ? "list" : [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:8081",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    ignoreHTTPSErrors: true,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
});
