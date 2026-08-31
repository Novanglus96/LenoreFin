/**
 * The Savings Plan page, driven in a real browser.
 *
 * These exist because of a specific blind spot, not for coverage. A Vue
 * template that reads a key the API does not send fails silently in every
 * other check we run: the page compiles, eslint is clean, `npm run build`
 * succeeds, and all 774 backend tests pass while the name column renders
 * empty and the bucket form posts a field the schema rejects. Both of those
 * shipped. Only a browser sees them.
 *
 * So the assertions here are deliberately about *what a person sees* — that a
 * row has a name, that a saved edit comes back — rather than about payload
 * shapes, which the API tests already pin.
 */
import { expect, test } from "@playwright/test";
import { login } from "./auth.js";

test.beforeEach(async ({ page }) => {
  await login(page);
  await page.goto("/planning/savings-plan");
  // The plan projects a year across every account, so the table arrives late.
  await expect(page.getByText("Allocates per paycheck")).toBeVisible();
});

test("every row in the plan is named", async ({ page }) => {
  const names = page.locator("table tbody tr td:first-child");
  await expect.poll(() => names.count()).toBeGreaterThan(0);

  for (let i = 0; i < (await names.count()); i += 1) {
    const text = (await names.nth(i).innerText()).trim();
    expect(text, `row ${i} has no bucket name`).not.toBe("");
  }
});

test("an inactive bucket is still listed and still reachable", async ({
  page,
}) => {
  // The plan only solves active buckets. Driving the table from the plan's
  // lines instead of the bucket list would hide every inactive one, and with
  // no second table on the page hidden means unreachable — there would be no
  // way to switch one back on.
  const row = page.locator("tbody tr", { hasText: "Charity" });
  await expect(row).toBeVisible();
  await expect(row).toContainText("Inactive, so the plan does not fund it.");
});

test("a bucket round trips through the form", async ({ page }) => {
  const name = `E2E ${Date.now()}`;

  await page.getByRole("button", { name: /add bucket/i }).click();
  await page.getByLabel("Bucket").fill(name);
  await page.getByLabel(/paycheck/i).first().fill("25.00");
  await page.getByRole("button", { name: /^save$|^add$|^submit$/i }).click();

  const row = page.locator("tbody tr", { hasText: name });
  await expect(row).toBeVisible();
  // The figure has to survive the save. An edit form that loads a field name
  // the API no longer sends comes back blank here, which is how that bug
  // presented the first time.
  await expect(row).toContainText("$25.00");

  await row.getByRole("button").first().click();
  await expect(page.getByLabel("Bucket")).toHaveValue(name);
  await page.getByLabel(/paycheck/i).first().fill("30.00");
  await page.getByRole("button", { name: /^save$|^update$|^submit$/i }).click();
  await expect(
    page.locator("tbody tr", { hasText: name }),
  ).toContainText("$30.00");

  // Clean up: these run against the dev database, which holds a copy of real
  // data, so a test that leaves rows behind poisons the next run's plan.
  await page.locator("tbody tr", { hasText: name }).getByRole("button").last().click();
  await page.getByRole("button", { name: /^delete$/i }).click();
  await expect(page.locator("tbody tr", { hasText: name })).toHaveCount(0);
});

test("the windfall rules card is named for windfalls", async ({ page }) => {
  // It was labelled "Per Paycheck Overage Rules", and a rename briefly moved
  // "Windfall Rules" onto the buckets table instead.
  await expect(
    page.getByText("Windfall Rules", { exact: true }),
  ).toBeVisible();
});
