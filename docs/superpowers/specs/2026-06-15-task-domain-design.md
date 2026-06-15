# Task Domain Design

- **Status:** Finalized
- **Date:** 2026-06-15
- **Scope:** The `apps.tasks` domain for the Internal Task Management tool
- **Owner:** phuc.luu@stanyangroup.com

---

## 1. Context & framing

Internal Task Management is a Django 6 + Django REST Framework backend on PostgreSQL.
The Task domain is built in the `apps.tasks` app (currently a stub) and depends on two
existing apps:

- **`apps.users`** — custom user model `users.User`. Always resolve it via
  `get_user_model()`, never by direct import. Carries the global `User.is_admin` flag.
- **`apps.teams`** — `teams.Team` plus the `teams.TeamMembership` through model whose
  `role` field (`leader` / `member`) defines per-team roles. A user can lead one team and
  be a member of another.

**Role model recap:**

- **admin** — global, cross-team, via `User.is_admin`. Sees and can do everything.
- **leader** — per-team, via `TeamMembership.role == "leader"`. Powers are scoped to the
  team(s) they lead.
- **member** — per-team, via `TeamMembership.role == "member"`.

Reused permission classes in `apps/users/permissions.py`: `IsAdmin`, `IsTeamLeader`,
`IsTeamMember`. New task-specific permission classes live in `apps/tasks/permissions.py`.

### Conventions this design follows

- User-facing strings (error messages, action labels) live in `apps/tasks/constants.py`.
- Serializers use explicit `validate_<field>()` methods and a cross-field `validate()`,
  all with type hints (e.g. `def validate_due_date(self, value: datetime) -> datetime:`).
- Views use DRF generics for simple CRUD; `APIView` (or generic action views) for the
  custom transition and nested-resource endpoints.
- One `urls.py` per app, with `name=` on every route, included from `core/urls.py`.
- Enum DB values are snake_case, matching the existing `teams.TeamMembership.Role`
  (`"leader", "Leader"`) convention: lowercase value, human label.

---

## 2. Goal

Build the Task domain as **6 incremental PRs**, each following TDD red → green with a
pre-commit review pause. The build order, dependencies, and per-PR contents are defined in
section 9 and mirrored in `ROADMAP.md`.

---

## 3. Data model

Six models. All FKs to the user model use `get_user_model()` / `settings.AUTH_USER_MODEL`.

### 3.1 `Task` (core)

| Field | Type | Rules / notes |
|---|---|---|
| `title` | `CharField(max_length=200)` | required |
| `description` | `TextField(blank=True, default="")` | optional |
| `status` | `CharField(choices=Status.choices)` | `TextChoices` (see below); default `NEW` |
| `priority` | `PositiveSmallIntegerField(choices=Priority.choices)` | `IntegerChoices`; default `NONE` (0); `db_index=True` |
| `estimate_hours` | `DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)` | `MinValueValidator(Decimal("0.01"))`; estimate only; `NULL` = "not estimated", distinct from `0` |
| `assignee` | `FK → user` | `null=True, blank=True, on_delete=SET_NULL, related_name="assigned_tasks"` |
| `created_by` | `FK → user` | required (non-null), `on_delete=PROTECT, related_name="created_tasks"` |
| `team` | `FK → teams.Team` | required, `on_delete=CASCADE, related_name="tasks"` (owning team) |
| `due_date` | `DateTimeField(null=True, blank=True)` | optional |
| `created_at` | `DateTimeField(auto_now_add=True)` | |
| `updated_at` | `DateTimeField(auto_now=True)` | |

- **`Meta.ordering = ["-created_at"]`** — deterministic fallback only. The real UX sort
  (priority DESC, then `due_date`) is applied at the query / API layer, not in `Meta`.
- **`PROTECT` on `created_by`** enforces the rule *"a user who created any task cannot be
  deleted"* — deletion of such a user is blocked at the DB/ORM layer.

**`Status` (`TextChoices`)** — snake_case DB values, human labels:

| Member | DB value | Label |
|---|---|---|
| `NEW` | `new` | New |
| `IN_PROGRESS` | `in_progress` | In Progress |
| `IN_REVIEW` | `in_review` | In Review |
| `DONE` | `done` | Done |
| `REJECTED` | `rejected` | Rejected |

**`Priority` (`IntegerChoices`)** — integer values so it sorts and filters numerically:

| Member | Value | Label |
|---|---|---|
| `NONE` | 0 | No priority |
| `LOW` | 1 | Low |
| `MEDIUM` | 2 | Medium |
| `HIGH` | 3 | High |
| `URGENT` | 4 | Urgent |

**`is_overdue` — derived, NOT a stored column.** Computed read-only:

```
is_overdue = (due_date is not NULL) AND (due_date < now()) AND (status != DONE)
```

Exposed in the API as a read-only boolean and supported as a list filter. Implemented as a
model property for single-object serialization and as a queryset annotation (e.g.
`Case/When` over `due_date`/`status`) for list filtering, so filtering happens in the DB.

### 3.2 `SubTask` (lightweight checklist item)

No own lifecycle, comments, or attachments — it is a checklist row on a parent task.

| Field | Type | Rules / notes |
|---|---|---|
| `parent_task` | `FK → Task` | `on_delete=CASCADE, related_name="subtasks"` |
| `title` | `CharField(max_length=200)` | required |
| `assignee` | `FK → user` | `null=True, blank=True, on_delete=SET_NULL, related_name="assigned_subtasks"` |
| `is_done` | `BooleanField(default=False)` | |
| `order` | `PositiveIntegerField(default=0)` | manual ordering |
| `created_at` / `updated_at` | timestamps | |

- `Meta.ordering = ["order", "id"]`.

### 3.3 `TaskComment`

| Field | Type | Rules / notes |
|---|---|---|
| `task` | `FK → Task` | `on_delete=CASCADE, related_name="comments"` |
| `author` | `FK → user` | `null=True, on_delete=SET_NULL, related_name="+"` |
| `body` | `TextField` | required |
| `created_at` / `updated_at` | timestamps | |

- `Meta.ordering = ["created_at"]`.
- **Moderation:** author can edit/delete their own comment; leader (of the task's team) and
  admin can moderate (edit/delete) any comment.

### 3.4 `TaskLink`

| Field | Type | Rules / notes |
|---|---|---|
| `task` | `FK → Task` | `on_delete=CASCADE, related_name="links"` |
| `url` | `URLField` | required |
| `label` | `CharField(max_length=200, blank=True)` | optional |
| `added_by` | `FK → user` | `null=True, on_delete=SET_NULL, related_name="+"` |
| `created_at` | timestamp | |

### 3.5 `TaskAttachment` (images only, ≤ 5 MB)

| Field | Type | Rules / notes |
|---|---|---|
| `task` | `FK → Task` | `on_delete=CASCADE, related_name="attachments"` |
| `image` | `ImageField(upload_to="task_attachments/%Y/%m/")` | requires Pillow |
| `caption` | `CharField(max_length=200, blank=True)` | optional |
| `added_by` | `FK → user` | `null=True, on_delete=SET_NULL, related_name="+"` |
| `created_at` | timestamp | |

**Validation:**

- Max size **5 MB** (`5 * 1024 * 1024`) via a custom validator.
- `ImageField` (backed by Pillow) guarantees the upload is a valid image.
- Restrict to common web image types: **jpeg, png, gif, webp**.

### 3.6 `TaskActivity` (immutable audit feed)

| Field | Type | Rules / notes |
|---|---|---|
| `task` | `FK → Task` | `on_delete=CASCADE, related_name="activities"` |
| `actor` | `FK → user` | `null=True, on_delete=SET_NULL, related_name="+"` |
| `action` | `CharField(choices=Action.choices)` | `TextChoices` (see below) |
| `metadata` | `JSONField(default=dict, blank=True)` | structured payload (see examples) |
| `created_at` | timestamp | |

- `Meta.ordering = ["-created_at"]`.

**`Action` (`TextChoices`)** values:
`created`, `status_changed`, `assigned`, `unassigned`, `validated`, `comment_added`,
`attachment_added`, `link_added`, `subtask_added`, `subtask_completed`.

**`metadata` examples:**

- status change: `{"from": "in_progress", "to": "in_review"}`
- validation: `{"decision": "rejected", "reason": "…"}`
- assignment: `{"assignee_id": 42}`

**Immutability:** there are **no update or delete endpoints** for activities. Rows are
written only through a single helper, `record_activity(task, actor, action, **metadata)`,
called from the action sites (create, transition, assign, comment/link/attachment/subtask
mutations). The feed is read-only over the API.

---

## 4. Lifecycle & validation (state machine)

```
   NEW ──start──▶ IN_PROGRESS ──submit──▶ IN_REVIEW ──accept──▶ DONE
                       ▲                       │
                       │                       │
                    restart                reject(reason)
                       │                       │
                       │                       ▼
                       └────────────────── REJECTED
```

| Transition | Endpoint | Actor | From → To | Extra rules |
|---|---|---|---|---|
| start | `POST /api/tasks/{id}/start/` | assignee | NEW → IN_PROGRESS | task must already have an assignee |
| submit | `POST /api/tasks/{id}/submit/` | assignee | IN_PROGRESS → IN_REVIEW | — |
| accept | `POST /api/tasks/{id}/accept/` | leader / admin | IN_REVIEW → DONE | terminal; validator rule (below) |
| reject | `POST /api/tasks/{id}/reject/` | leader / admin | IN_REVIEW → REJECTED | **reason required**; recorded in the `validated` activity metadata; validator rule |
| restart | `POST /api/tasks/{id}/restart/` | assignee / leader | REJECTED → IN_PROGRESS | — |

- **DONE is terminal.** No transition leaves `DONE`.
- **Validator rule (separation of duties):** `accept` and `reject` require the actor to be
  a **leader of the task's team** (or an admin), and the actor **cannot validate a task on
  which they are the assignee**.
- **`reject` requires a reason**; the reason is stored in the `validated` `TaskActivity`
  metadata: `{"decision": "rejected", "reason": "<text>"}`. `accept` records
  `{"decision": "accepted"}`.

**Each transition is its own endpoint** (`/start`, `/submit`, `/accept`, `/reject`,
`/restart`) — deliberately not a "magic" `PATCH status`. This keeps each transition's
permission check and side-effects (reject reason, activity emit) explicit and individually
testable.

---

## 5. RBAC matrix

| Action | member | leader | admin |
|---|:--:|:--:|:--:|
| Create task in own team | yes | yes | yes |
| Set descriptive fields (priority / estimate / due / description) on own or created task | yes | yes | yes |
| Assign task to **another** member | no (self-assign only) | yes | yes |
| start / submit own assigned task | yes | yes | yes |
| Validate (accept / reject) | no | yes (own team, not own task) | yes |
| Edit / delete task | creator only | yes | yes |
| Comment / link / attach / add subtask | yes | yes | yes |

- **admin** is global across all teams.
- **leader** powers are scoped to the team(s) they lead, via per-team membership.
- **member** may self-assign (set themselves as `assignee`) but may not assign others.
- "Edit / delete task" for members is limited to tasks they created; leaders and admins may
  edit/delete any task in their scope.

---

## 6. Visibility / list scoping

`GET /api/tasks/` is a **shared team board** (not a personal task list):

- **member** — sees **all** tasks in the team(s) they belong to.
- **leader** — sees the tasks of the team(s) they lead.
- **admin** — sees **all** tasks across all teams.

Scoping is enforced by filtering the queryset against the requesting user's memberships
(and `is_admin`), so out-of-scope tasks are never returned.

---

## 7. API surface

| Resource | Endpoint(s) | Notes |
|---|---|---|
| Task list / create | `GET, POST /api/tasks/` | filters: `status`, `priority`, `assignee`, `is_overdue`; search by `title` |
| Task detail | `GET, PUT, PATCH, DELETE /api/tasks/{id}/` | retrieve / update / delete |
| Transitions | `POST /api/tasks/{id}/{start\|submit\|accept\|reject\|restart}/` | one endpoint per transition |
| Subtasks | `GET, POST /api/tasks/{id}/subtasks/` · `PATCH, DELETE /api/tasks/{id}/subtasks/{sub_id}/` | update `is_done` / `assignee`, delete |
| Comments | `GET, POST /api/tasks/{id}/comments/` · `PATCH, DELETE /api/tasks/{id}/comments/{comment_id}/` | author edits own; leader/admin moderate |
| Links | `GET, POST /api/tasks/{id}/links/` · `DELETE /api/tasks/{id}/links/{link_id}/` | |
| Attachments | `GET, POST /api/tasks/{id}/attachments/` · `DELETE /api/tasks/{id}/attachments/{att_id}/` | multipart upload; image ≤ 5 MB |
| Activity | `GET /api/tasks/{id}/activity/` | read-only list |

Pagination and advanced search/filter are deferred to roadmap **Epic E**.

---

## 8. Infrastructure additions

- **Pillow** — add via `uv add Pillow` and rebuild the backend image; required for
  `ImageField`.
- **Media storage** — configure `MEDIA_ROOT` / `MEDIA_URL`, backed by a **mounted Docker
  volume** so uploads persist across container restarts.
- **Attachment validator** — enforce 5 MB limit + image content-type (jpeg/png/gif/webp).
- **Dev media serving** via Django's static/media serving in development.
  Production-grade serving (nginx / object storage) is **deferred**.

---

## 9. Decomposition into PRs

Each PR is TDD red → green with a pre-commit review pause.

| PR | Title | Contents |
|---|---|---|
| **1** | Core Task + CRUD | `Task` model, serializer, list/create/retrieve/update/delete, RBAC + visibility scoping, `is_overdue` derived. *Revises/replaces the paused B1 model tests.* |
| **2** | Assignment + lifecycle / validation | transition endpoints, assign/unassign, reject-reason, separation-of-duties. |
| **3** | Activity log | `TaskActivity` model + `record_activity` helper; emit `created` / `status_changed` / `assigned` / `validated` from the PR 1–2 action sites. |
| **4** | Subtasks | `SubTask` model + endpoints; emit `subtask_added` / `subtask_completed`. |
| **5** | Comments | `TaskComment` model + endpoints; emit `comment_added`. |
| **6** | Links + image attachments | `TaskLink` + `TaskAttachment` models + endpoints + Pillow/media infra; emit `link_added` / `attachment_added`. |

**Dependency order:** PR 1 → PR 2 (lifecycle needs the model + CRUD). PR 3 depends on
PR 1 + PR 2 (it emits events from their action sites). PRs 4, 5, and 6 each depend on PR 1
(core CRUD) and emit their activities through the PR 3 helper.

---

## 10. Deferred (YAGNI)

Recorded explicitly so the boundary is intentional, not accidental:

- Worklogs / actual-hours tracking (the model is estimate-only).
- Subtask own lifecycle (subtasks stay lightweight checklist rows).
- Auto-rollup of parent completion from subtask state.
- Configurable priority schemes (priority is a fixed 0–4 enum).
- Non-image file uploads (attachments are images only).
- Email / notifications (roadmap **Epic H**).
- Pagination / advanced search (roadmap **Epic E**).
- Frontend (roadmap **Epic I**).

---

## 11. Open decisions (resolved)

| Question | Decision |
|---|---|
| Who may create a task? | **Any member in their own team** (Option A). |
| How is completion validated? | **Leader sign-off** — team-scoped, and a leader cannot validate a task they are assigned to. |
| How is "overdue" represented? | **Derived** (computed property/annotation), not a stored status column. |
| How rich are subtasks? | **Lightweight** checklist items — no own lifecycle, comments, or attachments. |
| How is history tracked? | **Explicit activity events** via `record_activity`, immutable feed. |
| How are attachments handled? | **Split** into `TaskLink` (URLs) and `TaskAttachment` (images ≤ 5 MB). |
| May members edit task fields? | **Yes** — members may set descriptive fields (priority/estimate/due/description) on their own/created tasks. |
| What is task visibility? | **Shared team board** — scoped to the user's team membership (admin sees all). |
