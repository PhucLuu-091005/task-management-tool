# Task Reminder Notifications — daily digest + scheduled overdue flip

**Date:** 2026-07-05
**Status:** Approved (design) — ready for implementation plan
**Branch:** `feat/task-reminders` (off `master`)

## Context & goal

"Overdue" is treated as a **stored `status` column** that is the source of truth for the
dashboard and list views (decided separately; the stats endpoint already reads it). That decision
is only justified if the transition into overdue carries a real **side effect** — otherwise a
stored+cron-flipped status is just a stale cache of `due_date < now()`.

This feature adds that side effect: a **daily 08:30 reminder email** to the people responsible for
a task, and schedules the existing midnight overdue flip so the stored status stays current. The
email is proactive — it warns people *before* the deadline (tasks due today) and keeps nagging
while a task stays overdue.

## Decisions (from design dialogue)

| # | Question | Decision |
|---|----------|----------|
| Q1 | Who receives the email? | **Reuse `recipients_for_assignment`** — user→the user; team→team leader(s); department→the department lead. Same audience as the assignment email. |
| Q2 | Dedup / once-per-task? | **No `notified_at` flag.** The digest recurs each morning while a task is still due-today or overdue; recurrence is intended. |
| Q3 | Email scope | **Digest (B):** per recipient, covering **due-today (not done)** + **still-overdue (not done)** tasks. |
| Q4 | Scheduling mechanism | **Cron sidecar container** in `docker-compose`, running `crond` with two repo-versioned schedules. No Celery/Redis. |

## Behavior — two scheduled jobs (Asia/Ho_Chi_Minh)

- **00:00** — `flip_overdue_tasks` (existing command): tasks with `due_date` past and status not in
  {`done`, `overdue`} → `overdue`. Maintains the stored-status source of truth.
- **08:30** — `send_task_reminders` (new command): one **per-recipient digest** email of that
  person's due-today and still-overdue tasks.

Lifecycle: due today → 08:30 heads-up → if still not done → flipped `overdue` at next midnight →
recurs in the digest every morning until done/closed.

## Recipient resolution & grouping

- Per task, resolve recipients with the existing `recipients_for_assignment(task)`
  (user→the user; team→`TeamMembership` leaders; department→`Department.lead`).
- **Invert** into a per-recipient digest: walk all candidate tasks, resolve recipients per task,
  accumulate into `recipient → {due_today: [Task], overdue: [Task]}`.
- **Dedupe** recipients (a user who leads two teams gets **one** email covering all their tasks).
- **Drop** recipients with no email address.
- **No actor exclusion** (scheduled job — there is no acting user).

## Task buckets (timezone-correct)

Boundaries are computed in **Asia/Ho_Chi_Minh** even though `TIME_ZONE=UTC`, so a task due 23:30
local counts as today, not tomorrow.

- **overdue** = `status == Task.Status.OVERDUE`.
- **due_today** = `due_date` in `[local_today_start, local_tomorrow_start)` **and**
  `status in {NEW, IN_PROGRESS}`.

A task due earlier *today* but not yet flipped (flip only runs at midnight) still falls in
**due_today** — acceptable; the digest lists it under "due today".

## Components & files (all in the `notifications` app for cohesion)

- `apps/notifications/services.py`
  - `build_reminder_digests() -> dict[User, dict]` — selects buckets, resolves + inverts recipients.
  - `send_task_reminders() -> int` — renders and sends one email per recipient; returns email count.
  - **Synchronous send.** A cron batch process exits as soon as the command returns, so the existing
    daemon-thread `_dispatch` would be killed mid-send. Reminders call `send_mail` synchronously
    (also lets tests assert on `mail.outbox`).
- `apps/notifications/management/commands/send_task_reminders.py` — thin wrapper: call
  `send_task_reminders()`, print the count.
- `apps/notifications/constants.py` — add `TASK_REMINDER_SUBJECT`, `TASK_REMINDER_TEMPLATE`.
- `apps/notifications/templates/notifications/task_reminder.txt` — Vietnamese digest: a
  "Đến hạn hôm nay" section and a "Quá hạn" section, each task linking to `FRONTEND_URL/tasks/{id}`.
- `core/settings/base.py` + `backend/.env.example` — ensure `EMAIL_*` + `FRONTEND_URL` present
  (verify against `master`; add if missing).
- `docker-compose.yml` — new **`cron`** service reusing the backend image, running `crond` with a
  repo-versioned crontab (two lines), `TZ=Asia/Ho_Chi_Minh`, sharing the backend `env_file`.

## Data model impact

None. No new fields or migrations (Q2 → no notified flag).

## Scheduling (cron sidecar)

- One extra compose service based on the backend image; command runs `crond` in the foreground.
- Repo-versioned crontab, two entries: `0 0 * * *` → `flip_overdue_tasks`;
  `30 8 * * *` → `send_task_reminders`.
- `TZ=Asia/Ho_Chi_Minh` on the container so cron interprets local time.
- **Implementation detail for the plan:** `crond` runs jobs with a minimal environment; the DB
  credentials from `env_file` must be made available to the job (e.g. an entrypoint that exports the
  container env into the cron job's environment, or a wrapper script). To be resolved in the plan.

## Testing (TDD, in Docker, `locmem` email backend)

- **Service**
  - bucket selection: due-today includes earlier-today; overdue = stored status; `done` excluded.
  - tz boundary: task due 23:30 local is "today", not tomorrow.
  - grouping/dedup: leader of two teams → one email; department lead; direct user assignee.
  - recipients with no email are skipped.
  - nothing due/overdue → 0 emails sent.
- **Command**: runs the service, emits the count; assert on `mail.outbox`.

## Scope, branch & PR

- One coherent requirement → one PR: **`feat/task-reminders`** off `master`.
- TDD red/green commits per unit (tests → service/command → template/constants → settings →
  compose sidecar).

## Out of scope / follow-ups

1. **Reconcile the list `?is_overdue` filter onto stored status** — the list currently derives
   overdue live from `due_date`, diverging from the stored-status source of truth. **Planned as the
   next PR after this feature** (its own small spec/plan).
2. PR16 (`feat/dashboard-stats`) doc-comment + review replies — already staged, tracked separately.

## Open questions

- Confirm `Asia/Ho_Chi_Minh` is the intended business timezone for "midnight"/"08:30"/"today"
  (assumed yes for a VN team).
