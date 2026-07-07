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

  const statusSelect = page.getByRole("combobox", { name: `Trạng thái: ${title}` });
  await expect(statusSelect).toHaveValue("new");

  await statusSelect.selectOption("in_progress");
  await expect(statusSelect).toHaveValue("in_progress");

  await statusSelect.selectOption("done");
  await expect(statusSelect).toHaveValue("done");
});
