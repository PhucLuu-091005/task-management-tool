import { test, expect } from "@playwright/test";

import { ADMIN, ADMIN_DISPLAY_NAME } from "./admin";
import { login, createTask } from "./helpers";

// Only admins/leaders may create tasks (README §5), so this path runs as the
// seeded admin, who assigns the task to themselves and drives its status.
test("create a task and move it through its status lifecycle", async ({ page }) => {
  await login(page, ADMIN);

  const title = `E2E task ${Date.now()}`;
  await createTask(page, { title, assigneeLabel: ADMIN_DISPLAY_NAME });
  await expect(page.getByRole("heading", { name: title })).toBeVisible();

  await page.getByRole("link", { name: "Công việc" }).first().click();
  await expect(page).toHaveURL(/\/tasks$/);
  await expect(page.getByRole("link", { name: title })).toBeVisible();

  // The list status control is a pill that opens its allowed transitions.
  const row = page.getByRole("link", { name: title }).locator("../..");
  const status = row.getByRole("button", { name: "Đổi trạng thái" });
  await expect(status).toContainText("Mới");

  await status.click();
  await page.getByRole("menuitem", { name: "Đang xử lý" }).click();
  // The one-way transition is confirmed before it applies.
  await page.getByRole("button", { name: "Chuyển" }).click();
  await expect(status).toContainText("Đang xử lý");

  await status.click();
  await page.getByRole("menuitem", { name: "Hoàn thành" }).click();
  await page.getByRole("button", { name: "Chuyển" }).click();

  // A terminal status renders as a plain badge — the menu button is gone.
  await expect(row.getByRole("button", { name: "Đổi trạng thái" })).toHaveCount(0);
  await expect(row.getByText("Hoàn thành")).toBeVisible();
});
