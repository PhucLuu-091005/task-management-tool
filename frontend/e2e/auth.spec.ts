import { test, expect } from "@playwright/test";

import { register, login } from "./helpers";

test("register, sign out, and sign back in", async ({ page }) => {
  const user = await register(page);
  await expect(page.getByRole("heading", { name: "Công việc" })).toBeVisible();

  await page.getByRole("button", { name: "Đăng xuất" }).click();
  await expect(page).toHaveURL(/\/login$/);

  await login(page, user);
  await expect(page.getByRole("heading", { name: "Công việc" })).toBeVisible();
});

test("guests are redirected to login", async ({ page }) => {
  await page.goto("/tasks");
  await expect(page).toHaveURL(/\/login$/);
});
