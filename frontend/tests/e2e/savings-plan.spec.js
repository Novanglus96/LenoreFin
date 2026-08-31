/**
 * The Savings Plan page, driven in a real browser.
 *
 * These exist for a specific blind spot, not for coverage. A Vue template that
 * reads a key the API does not send fails silently in every other check we
 * run: the page compiles, eslint is clean, `npm run build` succeeds, and all
 * 774 backend tests pass while the name column renders empty and the bucket
 * form posts a field the schema rejects. Both of those shipped.
 *
 * So the assertions are about what a person sees — that a row has a name, that
 * a saved edit comes back — rather than payload shapes, which the API tests
 * already pin.
 */
import { expect, test } from "@playwright/test";
import { login, openSavingsPlan } from "./auth.js";

test.beforeEach(async ({ page }) => {
  await login(page);
  await openSavingsPlan(page);
});

test("every row in the plan is named", async ({ page }) => {
  const names = page.locator("table").first().locator("tbody tr td:first-child");
  const count = await names.count();
  expect(count).toBeGreaterThan(0);

  for (let i = 0; i < count; i += 1) {
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
  // Its stored contribution still shows; only the plan's columns are blank.
  await expect(row).toContainText("$15.00");
});

test("a bucket round trips through the form", async ({ page }) => {
  const name = `E2E ${Date.now()}`;

  await page.locator(".mdi-pail-plus").first().click();
  const form = page.locator(".v-dialog .v-card").first();
  await form.getByLabel("Bucket").fill(name);
  await form.getByLabel("Paycheck(per)").fill("25.00");
  await form.getByRole("button", { name: "Add Bucket" }).click();

  const row = page.locator("tbody tr", { hasText: name });
  await expect(row).toBeVisible({ timeout: 60_000 });
  // The figure has to survive the save. An edit form that loads a field the
  // API no longer sends comes back blank here, which is how that bug presented.
  await expect(row).toContainText("$25.00");

  await row.locator(".mdi-pencil").click();
  const edit = page.locator(".v-dialog .v-card").first();
  await expect(edit.getByLabel("Bucket")).toHaveValue(name);
  await expect(edit.getByLabel("Paycheck(per)")).toHaveValue("25.00");
  await edit.getByLabel("Paycheck(per)").fill("30.00");
  await edit.getByRole("button", { name: "Save Changes" }).click();
  await expect(page.locator("tbody tr", { hasText: name })).toContainText(
    "$30.00",
    { timeout: 60_000 },
  );

  // Clean up: these run against the dev database, which holds a copy of real
  // data, so a test that leaves rows behind poisons the next run's plan.
  await page.locator("tbody tr", { hasText: name }).locator(".mdi-delete").click();
  await page.getByRole("button", { name: "Delete", exact: true }).click();
  await expect(page.locator("tbody tr", { hasText: name })).toHaveCount(0, {
    timeout: 60_000,
  });
});

test("the windfall rules card is named for windfalls", async ({ page }) => {
  // It was labelled "Per Paycheck Overage Rules", and a rename briefly moved
  // "Windfall Rules" onto the buckets table instead.
  await expect(page.getByText("Windfall Rules", { exact: true })).toBeVisible();
});
