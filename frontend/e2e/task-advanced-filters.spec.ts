import { test, expect } from "@playwright/test";

import { ADMIN, ADMIN_DISPLAY_NAME } from "./admin";
import { login, createTask } from "./helpers";

test("assignee and overdue filters narrow the task list", async ({ page }) => {
  await login(page, ADMIN);

  const token = `flt${Date.now()}`;
  await createTask(page, {
    title: `${token} one`,
    assigneeLabel: ADMIN_DISPLAY_NAME,
  });
  await createTask(page, {
    title: `${token} two`,
    assigneeLabel: ADMIN_DISPLAY_NAME,
  });

  await page.goto("/tasks");
  const search = page.getByPlaceholder(/Tìm theo tiêu đề/);
  await search.fill(token);
  await search.press("Enter");

  const mine = page.getByRole("link", { name: new RegExp(token) });
  await expect(mine).toHaveCount(2);

  // Assignee filter: type = Người, then the admin. Both tasks are theirs, so
  // both survive — proving the assignee_user param passes through correctly.
  await page.getByLabel("Lọc theo loại người nhận").selectOption("user");
  await page
    .getByLabel("Lọc theo người")
    .selectOption({ label: ADMIN_DISPLAY_NAME });
  await expect(mine).toHaveCount(2);

  // Overdue toggle: neither task is overdue, so the list empties.
  await page.getByLabel("Trễ hạn").check();
  await expect(mine).toHaveCount(0);

  await page.getByLabel("Trễ hạn").uncheck();
  await expect(mine).toHaveCount(2);
});
