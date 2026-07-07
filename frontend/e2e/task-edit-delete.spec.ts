import { test, expect } from "@playwright/test";

import { ADMIN, ADMIN_DISPLAY_NAME } from "./admin";
import { login, createTask } from "./helpers";

test("edit a task's title, then delete it", async ({ page }) => {
  await login(page, ADMIN);

  const title = `E2E edit ${Date.now()}`;
  await createTask(page, { title, assigneeLabel: ADMIN_DISPLAY_NAME });
  await expect(page.getByRole("heading", { name: title })).toBeVisible();

  await page.getByRole("button", { name: "Chỉnh sửa" }).click();
  const newTitle = `${title} (updated)`;
  await page.locator("#title").fill(newTitle);
  await page.getByRole("button", { name: "Lưu thay đổi" }).click();
  await expect(page.getByRole("heading", { name: newTitle })).toBeVisible();

  // Delete opens a confirmation modal; confirm it. `exact` avoids matching any
  // per-item "Xoá liên kết" / "Xoá đính kèm" buttons.
  await page.getByRole("button", { name: "Xoá", exact: true }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Xoá" }).click();

  await expect(page).toHaveURL(/\/tasks$/);
  await expect(page.getByRole("link", { name: newTitle })).toHaveCount(0);
});
