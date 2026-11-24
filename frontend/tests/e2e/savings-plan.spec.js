// The savings plan, as a person sees it. Reads and edits only: accepting a
// plan or applying a windfall writes reminders and transactions into the
// shared dev database, so those paths are covered by the service tests.
import { expect, test } from "@playwright/test";
import { login, openSavingsPlan } from "./auth.js";

const money = text => Number(text.replace(/[^0-9.-]/g, ""));

test.beforeEach(async ({ page }) => {
  await login(page);
  await openSavingsPlan(page);
});

test("every bucket shows its account, its year and an outlook", async ({
  page,
}) => {
  const rows = page.locator('[data-testid^="plan-row-"]');
  await expect(rows.first()).toBeVisible();
  const count = await rows.count();
  expect(count).toBeGreaterThan(3);
  for (let i = 0; i < count; i++) {
    const row = rows.nth(i);
    // A row the template reads the wrong key for renders blank, not broken.
    await expect(row.locator("td").first()).not.toHaveText(/^\s*$/);
    const linked = !(await row.getByText("No account linked").count());
    if (linked) {
      await expect(row.locator("svg.plan-spark")).toBeVisible();
      await expect(row.getByText(/Ideal|Workable|Not solvent/)).toBeVisible();
    }
  }
  await expect(page.getByTestId("plan-verdict")).toHaveText(
    /Ideal|Workable|Not solvent/,
  );
  await expect(page.locator(".apexcharts-canvas")).toBeVisible();
  await expect(page.getByTestId("window-start")).toContainText(/\d{4}/);
});

test("editing an amount re-plans live, and reset puts it back", async ({
  page,
}) => {
  const total = page.getByTestId("plan-total");
  const before = money((await total.textContent()).split("(")[0]);
  const input = page.locator('[data-testid^="plan-amount-"] input').first();
  const current = Number(await input.inputValue());
  await input.fill(String(current + 100));
  await expect
    .poll(async () => money((await total.textContent()).split("(")[0]))
    .toBe(before + 100);
  await expect(total).toContainText("+$100.00");
  await page.getByTestId("plan-reset").click();
  await expect
    .poll(async () => money((await total.textContent()).split("(")[0]))
    .toBe(before);
});

test("a bucket can be drafted into the plan and dropped again", async ({
  page,
}) => {
  await page.getByTestId("plan-add-bucket").click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Name").fill("E2E Draft");
  await dialog.getByLabel("Account it lives in").click();
  await page.getByRole("option").first().click();
  await dialog.getByLabel("Per paycheck").fill("10");
  await dialog.getByRole("button", { name: "Add" }).click();
  const row = page.getByTestId("plan-row-E2E Draft");
  await expect(row).toBeVisible();
  await expect(row.getByText("new")).toBeVisible();
  await expect(row.locator("svg.plan-spark")).toBeVisible();
  await row.getByRole("button", { name: "Remove E2E Draft" }).click();
  await expect(row).toHaveCount(0);
});

test("a windfall gets a suggested split", async ({ page }) => {
  await page.getByTestId("windfall-amount").locator("input").fill("1000");
  await page.getByTestId("windfall-suggest").click();
  await expect(
    page.getByText(/Allocated \$[\d,.]+ of \$1,000\.00/),
  ).toBeVisible();
});

test("a bucket's revert button puts back its saved amount", async ({
  page,
}) => {
  const input = page.locator('[data-testid^="plan-amount-"] input').first();
  const testid = await page
    .locator('[data-testid^="plan-amount-"]')
    .first()
    .getAttribute("data-testid");
  const name = testid.replace("plan-amount-", "");
  const saved = await input.inputValue();
  await expect(page.getByTestId(`plan-revert-${name}`)).toHaveCount(0);
  await input.fill(String(Number(saved) + 25));
  await page.getByTestId(`plan-revert-${name}`).click();
  await expect(input).toHaveValue(saved);
  await expect(page.getByTestId(`plan-revert-${name}`)).toHaveCount(0);
});

test("an insolvent plan can be accepted only with an override", async ({
  page,
}) => {
  const verdict = await page.getByTestId("plan-verdict").textContent();
  test.skip(!/Not solvent/.test(verdict), "the dev data's plan is solvent");
  await page.getByTestId("plan-accept").click();
  const confirm = page.getByTestId("plan-accept-confirm");
  await expect(confirm).toBeDisabled();
  await page.getByTestId("plan-accept-override").locator("input").check();
  await expect(confirm).toBeEnabled();
  // Stop here: accepting writes reminders into the shared dev database.
  await page.getByRole("button", { name: "Cancel" }).click();
});
