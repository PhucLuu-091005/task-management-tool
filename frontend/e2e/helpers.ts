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
    // Full name must be unique per user (backend unique_full_name constraint),
    // so vary the given name by the same id used for username/email.
    firstName: `E2E ${id}`,
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

// Opens the create-task modal from the list, fills it, and leaves the page on
// the new task's detail view. Caller must already be signed in as someone
// allowed to create (admin/leader).
export async function createTask(
  page: Page,
  opts: { title: string; assigneeLabel: string; priority?: "low" | "medium" | "high" },
): Promise<void> {
  await page.goto("/tasks");
  await page.getByRole("button", { name: "Tạo công việc" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.locator("#title").fill(opts.title);
  if (opts.priority) await dialog.locator("#priority").selectOption(opts.priority);
  await dialog.locator("#assignee_user").selectOption({ label: opts.assigneeLabel });
  await dialog.getByRole("button", { name: "Tạo công việc" }).click();
  await expect(page).toHaveURL(/\/tasks\/\d+$/);
}
