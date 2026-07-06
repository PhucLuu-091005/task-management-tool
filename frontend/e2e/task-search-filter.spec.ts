import { test, expect } from "@playwright/test";

import { ADMIN, ADMIN_DISPLAY_NAME } from "./admin";
import { login, createTask } from "./helpers";

test("search and filters narrow the task list", async ({ page }) => {
  await login(page, ADMIN);

  // A unique token isolates this run's rows from every other task in the DB.
  const token = `srch${Date.now()}`;
  await createTask(page, {
    title: `${token} alpha`,
    assigneeLabel: ADMIN_DISPLAY_NAME,
    priority: "high",
  });
  await createTask(page, {
    title: `${token} beta`,
    assigneeLabel: ADMIN_DISPLAY_NAME,
    priority: "low",
  });

  await page.goto("/tasks");

  const search = page.getByPlaceholder(/Tìm theo tiêu đề/);
  await search.fill(token);
  await search.press("Enter");

  const mine = page.getByRole("link", { name: new RegExp(token) });
  await expect(mine).toHaveCount(2);

  // Priority filter → only the high-priority row survives.
  await page.getByLabel("Lọc theo độ ưu tiên").selectOption("high");
  await expect(page.getByRole("link", { name: `${token} alpha` })).toBeVisible();
  await expect(page.getByRole("link", { name: `${token} beta` })).toHaveCount(0);

  // Both rows are still "new", so filtering to "done" empties the list.
  await page.getByLabel("Lọc theo độ ưu tiên").selectOption("");
  await page.getByLabel("Lọc theo trạng thái").selectOption("done");
  await expect(mine).toHaveCount(0);
});
