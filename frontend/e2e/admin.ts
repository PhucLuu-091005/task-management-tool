import { TestUser } from "./helpers";

// Must match backend/apps/users/management/commands/seed_e2e.py defaults.
// globalSetup seeds this account (is_admin=True) so create/status tests have an
// author allowed to create tasks (README §5: only admins/leaders may create).
export const ADMIN: TestUser = {
  username: process.env.E2E_ADMIN_USERNAME ?? "e2eadmin",
  password: process.env.E2E_ADMIN_PASSWORD ?? "Passw0rd!e2e",
  email: process.env.E2E_ADMIN_EMAIL ?? "e2eadmin@example.com",
  lastName: "E2E",
  firstName: "Admin",
};

// Display name as the UI renders it: family name first.
export const ADMIN_DISPLAY_NAME = `${ADMIN.lastName} ${ADMIN.firstName}`;
