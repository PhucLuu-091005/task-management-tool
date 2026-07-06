import { execFileSync } from "node:child_process";

import { ADMIN } from "./admin";

// The admin account can't be provisioned over the API (there's no endpoint to
// grant is_admin), so seed it by running the management command inside the
// running backend container. Match the container publishing the API port so a
// second unrelated stack's `backend` service isn't picked; override with
// E2E_BACKEND_CONTAINER.
function backendContainer(): string {
  const explicit = process.env.E2E_BACKEND_CONTAINER;
  if (explicit) return explicit;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const port = new URL(apiUrl).port || "8000";
  const out = execFileSync(
    "docker",
    [
      "ps",
      "--filter",
      "label=com.docker.compose.service=backend",
      "--filter",
      `publish=${port}`,
      "--format",
      "{{.Names}}",
    ],
    { encoding: "utf8" },
  ).trim();
  const names = out.split("\n").filter(Boolean);
  if (names.length === 0) {
    throw new Error(
      `E2E setup: no running backend container publishing port ${port}. Start the ` +
        "stack (docker compose up -d db backend) or set E2E_BACKEND_CONTAINER.",
    );
  }
  return names[0];
}

export default function globalSetup() {
  // CI runs the backend directly (no Compose stack to exec into) and seeds the
  // admin with an explicit `manage.py seed_e2e` workflow step, so skip here.
  if (process.env.CI) return;

  const container = backendContainer();
  execFileSync(
    "docker",
    [
      "exec",
      "-e",
      `E2E_ADMIN_USERNAME=${ADMIN.username}`,
      "-e",
      `E2E_ADMIN_PASSWORD=${ADMIN.password}`,
      "-e",
      `E2E_ADMIN_EMAIL=${ADMIN.email}`,
      container,
      "uv",
      "run",
      "python",
      "manage.py",
      "seed_e2e",
    ],
    { stdio: "inherit" },
  );
}
