import { Page, expect } from "@playwright/test";

export interface TestUser {
  username: string;
  password: string;
  email: string;
  firstName: string;
  lastName: string;
}

// A fresh account per test keeps runs independent and needs no seed data:
// register() self-serves a non-admin who can assign tasks to themselves.
export function makeUser(): TestUser {
  // Username must be alphanumeric (backend rejects underscores/spaces).
  const id = `${Date.now()}${Math.floor(Math.random() * 1_000)}`;
  return {
    username: `e2e${id}`,
    password: "Passw0rd!e2e",
    email: `e2e${id}@example.com`,
    firstName: "E2E",
    lastName: "Tester",
  };
}

export async function register(page: Page, user: TestUser = makeUser()): Promise<TestUser> {
  await page.goto("/register");
  await page.locator("#last_name").fill(user.lastName);
  await page.locator("#first_name").fill(user.firstName);
  await page.locator("#email").fill(user.email);
  await page.locator("#username").fill(user.username);
  await page.locator("#password").fill(user.password);
  await page.locator("#confirm_password").fill(user.password);
  await page.getByRole("button", { name: "Đăng ký" }).click();
  await expect(page).toHaveURL(/\/tasks$/);
  return user;
}

export async function login(page: Page, user: TestUser): Promise<void> {
  await page.goto("/login");
  await page.locator("#username").fill(user.username);
  await page.locator("#password").fill(user.password);
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).toHaveURL(/\/tasks$/);
}

// Creates a task assigned to a user (by their display name in the dropdown) and
// leaves the page on the new task's detail view. Caller must already be signed in
// as someone allowed to create (admin/leader).
export async function createTask(
  page: Page,
  opts: { title: string; assigneeLabel: string; priority?: "low" | "medium" | "high" },
): Promise<void> {
  await page.goto("/tasks/new");
  await page.locator("#title").fill(opts.title);
  if (opts.priority) await page.locator("#priority").selectOption(opts.priority);
  await page.locator("#assignee_user").selectOption({ label: opts.assigneeLabel });
  await page.getByRole("button", { name: "Tạo công việc" }).click();
  await expect(page).toHaveURL(/\/tasks\/\d+$/);
}
