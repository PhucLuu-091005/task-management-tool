import { test, expect } from "@playwright/test";

import { ADMIN, ADMIN_DISPLAY_NAME } from "./admin";
import { login, register } from "./helpers";

test("admin manages departments, teams, and members", async ({ page }) => {
  await login(page, ADMIN);

  const token = `adm${Date.now()}`;
  const deptName = `Phòng ${token}`;
  const teamName = `Nhóm ${token}`;
  const dialog = page.getByRole("dialog");

  // --- Create a department ---
  await page.goto("/admin/departments");
  await page.getByRole("button", { name: "Tạo phòng ban" }).click();
  await dialog.locator("#dept-name").fill(deptName);
  await dialog.getByRole("button", { name: "Tạo" }).click();
  await expect(page.getByText(deptName)).toBeVisible();

  // --- Create a team in that department ---
  await page.goto("/admin/teams");
  await page.getByRole("button", { name: "Tạo nhóm" }).click();
  await dialog.locator("#team-name").fill(teamName);
  await dialog.locator("#team-dept").selectOption({ label: deptName });
  await dialog.getByRole("button", { name: "Tạo" }).click();

  // Row is scoped by the unique token so leftover data can't interfere.
  const row = page.locator(".divide-y > div").filter({ hasText: token });
  await expect(row).toBeVisible();
  // The creating admin is auto-added as a leader → one member.
  await expect(page.getByText(`${deptName} · 1 thành viên`)).toBeVisible();

  // --- Members: change the auto-added admin's role ---
  await row.getByRole("button", { name: "Thành viên" }).click();
  const roleSelect = dialog.getByRole("combobox", {
    name: `Vai trò của ${ADMIN_DISPLAY_NAME}`,
  });
  await expect(roleSelect).toHaveValue("leader");
  await roleSelect.selectOption("member");
  await expect(roleSelect).toHaveValue("member");
  await page.getByRole("button", { name: "Đóng" }).click();

  // --- Rename the team ---
  await row.getByRole("button", { name: "Sửa" }).click();
  await dialog.locator("#team-name").fill(`${teamName} v2`);
  await dialog.getByRole("button", { name: "Lưu" }).click();
  await expect(page.getByText(`${teamName} v2`)).toBeVisible();

  // --- Delete the team ---
  await row.getByRole("button", { name: "Xoá" }).click();
  await dialog.getByRole("button", { name: "Xoá" }).click();
  await expect(page.locator(".divide-y > div").filter({ hasText: token })).toHaveCount(
    0,
  );

  // --- Delete the (now empty) department ---
  await page.goto("/admin/departments");
  const deptRow = page.locator(".divide-y > div").filter({ hasText: token });
  await deptRow.getByRole("button", { name: "Xoá" }).click();
  await dialog.getByRole("button", { name: "Xoá" }).click();
  await expect(
    page.locator(".divide-y > div").filter({ hasText: token }),
  ).toHaveCount(0);
});

test("non-admins cannot reach the admin area", async ({ page }) => {
  await register(page);

  await expect(page.getByRole("link", { name: "Quản trị" })).toHaveCount(0);

  await page.goto("/admin/teams");
  await expect(page).toHaveURL(/\/tasks$/);
});
