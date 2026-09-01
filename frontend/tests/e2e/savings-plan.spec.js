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
  const names = page
    .locator("table")
    .first()
    .locator("tbody tr td:first-child");
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
  await form.getByLabel("Bucket", { exact: true }).fill(name);
  await form.getByLabel("Paycheck(per)").fill("25.00");
  await form.getByRole("button", { name: "Add Bucket" }).click();

  const row = page.locator("tbody tr", { hasText: name });
  await expect(row).toBeVisible({ timeout: 60_000 });
  // The figure has to survive the save. An edit form that loads a field the
  // API no longer sends comes back blank here, which is how that bug presented.
  await expect(row).toContainText("$25.00");

  await row.locator(".mdi-pencil").click();
  const edit = page.locator(".v-dialog .v-card").first();
  await expect(edit.getByLabel("Bucket", { exact: true })).toHaveValue(name);
  await expect(edit.getByLabel("Paycheck(per)")).toHaveValue("25.00");
  await edit.getByLabel("Paycheck(per)").fill("30.00");
  await edit.getByRole("button", { name: "Save Changes" }).click();
  await expect(page.locator("tbody tr", { hasText: name })).toContainText(
    "$30.00",
    { timeout: 60_000 },
  );

  // Clean up: these run against the dev database, which holds a copy of real
  // data, so a test that leaves rows behind poisons the next run's plan.
  await page
    .locator("tbody tr", { hasText: name })
    .locator(".mdi-delete")
    .click();
  await page.getByRole("button", { name: "Delete", exact: true }).click();
  await expect(page.locator("tbody tr", { hasText: name })).toHaveCount(0, {
    timeout: 60_000,
  });
});

// Vuetify's field wrapper swallows clicks aimed at the inner input, and its
// menu animates out, so a select is opened by its root and the next open waits
// for the previous overlay to go.
async function chooseMode(page, form, label) {
  const select = form.locator(".v-select").filter({
    hasText: "What this bucket is for",
  });
  // `.v-field`, not the select root: the root includes the persistent hint,
  // and once the hint grows to two lines the root's centre — where Playwright
  // clicks — lands on the hint text, which opens nothing.
  await select.locator(".v-field").click();
  const option = page.getByRole("option", { name: label });
  await option.waitFor({ state: "visible" });
  await option.click();
  // The menu animates out, and while its overlay is still in the DOM the scrim
  // swallows the next click on the select. Waiting for the element to go is
  // what makes a second mode change work. Scoped to `.v-menu`: the dialog the
  // form lives in is itself an active overlay and never detaches.
  await page.locator(".v-overlay--active.v-menu").waitFor({ state: "detached" });
}

test("a bucket's mode decides which figures the form asks for", async ({
  page,
}) => {
  // The whole point of a stated mode is that a field the plan would ignore is
  // never offered. Inferring intent from which boxes happened to be filled in
  // is what let one field mean two things at once.
  const name = `E2E Mode ${Date.now()}`;
  const balance = () =>
    form.getByRole("spinbutton", { name: "Balance to hold" });
  const goal = () => form.getByRole("spinbutton", { name: "Goal amount" });

  await page.locator(".mdi-pail-plus").first().click();
  const form = page.locator(".v-dialog .v-card").first();
  await form.getByLabel("Bucket", { exact: true }).fill(name);
  await form.getByLabel("Paycheck(per)").fill("25.00");

  // Cover asks for no balance at all.
  await expect(balance()).toHaveCount(0);
  await expect(goal()).toHaveCount(0);

  await chooseMode(page, form, "Maintain a balance");
  await expect(balance()).toBeVisible();
  await expect(goal()).toHaveCount(0);

  await chooseMode(page, form, "Reach a goal by a date");
  await expect(goal()).toBeVisible();
  await expect(form.getByLabel("Reach it by", { exact: true })).toBeVisible();
  // The balance field is gone, not merely hidden — a figure the mode ignores
  // must not be sitting there waiting to be sent.
  await expect(balance()).toHaveCount(0);

  await page.keyboard.press("Escape");
});

test("the windfall rules card is named for windfalls", async ({ page }) => {
  // It was labelled "Per Paycheck Overage Rules", and a rename briefly moved
  // "Windfall Rules" onto the buckets table instead.
  await expect(page.getByText("Windfall Rules", { exact: true })).toBeVisible();
});
