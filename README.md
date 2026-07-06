# Internal Task Management — Hệ thống quản lý công việc nội bộ

Ứng dụng web quản lý công việc cho phòng/nhóm: tạo việc, giao việc, theo dõi tiến độ và cập nhật trạng thái. Mục tiêu mô phỏng quy trình quản lý task trong doanh nghiệp, đồng thời là dự án học/thực hành full-stack với **Next.js (React) + Django + PostgreSQL**.

## 1. Tính năng chính

1. **Cơ cấu tổ chức:** quản lý **Phòng ban → Nhóm → Nhân viên** — 3 thực thể lồng nhau trong 1 công ty.
2. **Quản lý danh sách công việc:** thêm, sửa, xoá, tìm kiếm, lọc theo trạng thái.
3. **Giao việc** cho **một cá nhân, một nhóm, hoặc một phòng ban**. Khi giao cho nhóm/phòng ban, hệ thống gửi thông báo tới **lãnh đạo (leader)** của nhóm/phòng ban đó.
4. **Cập nhật trạng thái:** Tạo mới → Đang xử lý → Hoàn thành. Khi thời gian thực hiện vượt mốc `due_date` mà task chưa hoàn thành, **hệ thống tự động chuyển sang Quá hạn** (job định kỳ).
5. **Quản lý người dùng theo role:** `admin`, `leader`, `member`.
6. **Dashboard** thống kê số lượng công việc theo trạng thái / người phụ trách / nhóm / phòng ban.

### Điểm cộng (nice-to-have)
- Gửi email/thông báo khi được giao việc.
- Phân trang, tìm kiếm và lọc nâng cao.
- Biểu đồ thống kê công việc.

## 2. Kiến trúc tổng quan

```
┌──────────────┐      REST API (JSON)      ┌──────────────┐      ┌────────────┐
│  Next.js     │  ───────────────────────► │  Django REST │ ───► │ PostgreSQL │
│  (frontend)  │  ◄─────────────────────── │  Framework   │ ◄─── │            │
└──────────────┘        JWT auth           └──────────────┘      └────────────┘
        │                                          │
        │                                          └──► Celery beat + Redis (job quá hạn định kỳ; email/thông báo)
        └──► Trình duyệt người dùng
```

- **Frontend:** Next.js (App Router) + React, gọi API qua `fetch`/axios, dùng React Query để cache. UI bằng Tailwind CSS.
- **Backend:** Django + Django REST Framework (DRF), xác thực JWT (`djangorestframework-simplejwt`), phân quyền theo role.
- **Database:** PostgreSQL.
- **API docs:** Swagger/OpenAPI qua `drf-spectacular`.
- **Đóng gói:** Docker + Docker Compose (frontend, backend, db, và redis/celery nếu bật thông báo).

## 3. Tech stack

| Lớp | Công nghệ |
|-----|-----------|
| Frontend | Next.js, React, TypeScript, Tailwind CSS, React Query, Recharts (biểu đồ) |
| Backend | Python, Django, Django REST Framework, SimpleJWT, drf-spectacular |
| Database | PostgreSQL |
| Async (tùy chọn) | Celery + Redis (gửi email khi giao việc) |
| DevOps | Docker, Docker Compose |

## 4. Mô hình dữ liệu (data model)

### Cơ cấu tổ chức: Phòng ban → Nhóm → Nhân viên

> **Phạm vi:** ứng dụng phục vụ **một công ty** (single-tenant). "Công ty" là gốc ngầm định của
> toàn hệ thống, *chưa* tách thành bảng riêng. Nếu sau cần nhiều công ty, thêm bảng `Company` đứng
> trên `Department`. Ba thực thể **Phòng ban, Nhóm, Nhân viên** là **khác nhau** và lồng nhau:
> `Department 1—* Team 1—* User` (nhân viên thuộc nhóm, nhóm thuộc phòng ban).

#### Department (Phòng ban)
| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| id | int (PK) | |
| name | string | tên phòng ban, duy nhất |
| description | text | |
| lead | FK → User (null) | lãnh đạo phòng ban; nhận thông báo khi giao việc cho cả phòng |
| created_at / updated_at | datetime | tự động |

#### Team (Nhóm)
| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| id | int (PK) | |
| name | string | tên nhóm, duy nhất |
| department | FK → Department | nhóm thuộc về 1 phòng ban |
| description | text | |
| created_at / updated_at | datetime | tự động |

#### TeamMembership (Nhân viên ∈ Nhóm)
| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| user | FK → User | |
| team | FK → Team | |
| role | enum | `leader` \| `member` — **leader** của nhóm nhận thông báo khi giao việc cho nhóm |

> Phòng ban của một nhân viên suy ra từ `team.department`.

### User (mở rộng từ Django `AbstractUser`)
| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| id | int (PK) | |
| username / email | string | email dùng để đăng nhập & gửi thông báo |
| first_name / last_name | string | |
| is_admin | bool | quyền quản trị toàn hệ thống (vai trò `admin`) |
| role theo nhóm | — | `leader` / `member` qua `TeamMembership.role` |
| is_active | bool | |

> **Vai trò (role):** `admin` là cờ cấp hệ thống (`is_admin`); `leader` / `member` là vai trò
> **theo từng nhóm** qua `TeamMembership.role` — một người có thể là leader nhóm này, member nhóm khác.

### Task
| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| id | int (PK) | |
| title | string | bắt buộc |
| description | text | |
| status | enum | `new` \| `in_progress` \| `done` \| `overdue` |
| priority | enum | `low` \| `medium` \| `high` (tùy chọn) |
| assignee_type | enum | `user` \| `team` \| `department` — loại đối tượng được giao |
| assignee_user | FK → User (null) | set khi `assignee_type = user` |
| assignee_team | FK → Team (null) | set khi `assignee_type = team` |
| assignee_department | FK → Department (null) | set khi `assignee_type = department` |
| created_by | FK → User | người tạo |
| due_date | datetime | mốc deadline để tính quá hạn |
| created_at / updated_at | datetime | tự động |

> **Ràng buộc giao việc:** đúng **một** trong `assignee_user / assignee_team / assignee_department`
> được set, khớp với `assignee_type`. Khi giao cho **nhóm/phòng ban**, hệ thống tạo thông báo gửi
> tới **leader** của nhóm/phòng ban tương ứng (nhân viên trong đơn vị vẫn xem được việc của đơn vị mình).
>
> **Quy tắc quá hạn (tự động):** task có `due_date < now` và `status ∉ {done}` được **hệ thống tự
> động** chuyển `status = overdue` qua **job định kỳ** (Celery beat hoặc management command chạy theo
> lịch). Giữa hai lần chạy job, API có thể trả thêm cờ `is_overdue` suy ra tức thời để UI không bị trễ.

## 5. Phân quyền (RBAC)

Ba vai trò: **`admin`** (quản trị toàn hệ thống), **`leader`** (lãnh đạo nhóm/phòng), **`member`**
(nhân viên). Bảng dưới là quyết định thiết kế cho dự án (có thể điều chỉnh):

| Hành động | admin | leader | member |
|-----------|:---:|:---:|:---:|
| Quản lý phòng ban / nhóm (CRUD) | ✅ | ❌ | ❌ |
| Quản lý người dùng (CRUD) | ✅ | ❌ | ❌ |
| Tạo / sửa / xoá task | ✅ (mọi task) | ✅ (trong nhóm/phòng mình phụ trách) | ❌ (chỉ task mình tạo cho bản thân) |
| Giao việc cho cá nhân / nhóm / phòng ban | ✅ (bất kỳ) | ✅ (trong phạm vi nhóm/phòng mình) | ❌ |
| Nhận thông báo khi nhóm/phòng được giao việc | — | ✅ (leader của đơn vị) | ❌ |
| Cập nhật trạng thái task được giao | ✅ | ✅ | ✅ |
| Xem dashboard | toàn bộ | nhóm/phòng phụ trách | chỉ task của mình |

## 6. API chính (REST)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/auth/login/` | Đăng nhập, trả JWT |
| POST | `/api/auth/refresh/` | Làm mới token |
| GET/POST | `/api/users/` | Danh sách / tạo người dùng (admin) |
| GET/PUT/DELETE | `/api/users/{id}/` | Chi tiết / sửa / xoá người dùng |
| GET/POST | `/api/departments/` | Danh sách / tạo phòng ban (admin) |
| GET/PUT/DELETE | `/api/departments/{id}/` | Chi tiết / sửa / xoá phòng ban |
| GET/POST | `/api/teams/` | Danh sách / tạo nhóm |
| GET/PUT/DELETE | `/api/teams/{id}/` | Chi tiết / sửa / xoá nhóm + quản lý thành viên |
| GET/POST | `/api/tasks/` | Danh sách (phân trang, filter, search) / tạo task (giao cho user/team/department) |
| GET/PUT/PATCH/DELETE | `/api/tasks/{id}/` | Chi tiết / cập nhật / xoá task |
| PATCH | `/api/tasks/{id}/status/` | Cập nhật trạng thái |
| GET | `/api/dashboard/stats/` | Thống kê theo trạng thái / người phụ trách / nhóm / phòng ban |

Khi tạo task, body chứa `assignee_type` (`user`\|`team`\|`department`) cùng đúng một trong
`assignee_user` / `assignee_team` / `assignee_department`.

Query params cho `/api/tasks/`: `?status=`, `?assignee_type=`, `?assignee_user=`, `?team=`, `?department=`, `?search=`, `?page=`, `?ordering=`.

API docs: `GET /api/schema/swagger-ui/` (drf-spectacular).

## 7. Cấu trúc thư mục đề xuất

```
internal-task-management/
├── backend/                 # Django project
│   ├── config/              # settings, urls, wsgi
│   ├── apps/
│   │   ├── users/           # model User, auth, permissions
│   │   └── tasks/           # model Task, viewsets, serializers
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Next.js app
│   ├── app/                 # App Router (login, tasks, dashboard)
│   ├── components/
│   ├── lib/                 # api client, hooks
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 8. Chạy dự án với Docker

```bash
# Build và khởi động toàn bộ stack
docker compose up --build

# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# Swagger:   http://localhost:8000/api/schema/swagger-ui/
```

`docker-compose.yml` (phác thảo): các service `db` (postgres), `backend` (django), `frontend` (next), và tùy chọn `redis` + `worker` (celery).

Biến môi trường chính (`.env`): `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `EMAIL_HOST`/`EMAIL_*` (nếu bật thông báo), `NEXT_PUBLIC_API_URL`.

## 8.1. Chất lượng code — Ruff & pre-commit

Dự án dùng **Ruff** để lint + format (cấu hình ở `backend/pyproject.toml`). CI chạy
`ruff check` và `ruff format --check` trên mỗi push/PR.

Để bắt lỗi lint/format **trước khi commit** (cùng bộ rule với CI), cài pre-commit hook:

```bash
# Cài pre-commit (host) — chọn 1 cách
uv tool install pre-commit        # hoặc: pipx install pre-commit / brew install pre-commit

# Kích hoạt hook trong repo (đọc .pre-commit-config.yaml)
pre-commit install

# (tùy chọn) chạy thử trên toàn bộ file
pre-commit run --all-files
```

Sau khi `pre-commit install`, mỗi lần `git commit` sẽ tự chạy Ruff (`ruff-check --fix` +
`ruff-format`); nếu hook sửa file, commit bị chặn để bạn `git add` lại rồi commit tiếp.

## 8.2. Kiểm thử E2E (Playwright)

Bộ kiểm thử end-to-end bằng **Playwright** (đặt cùng frontend, thư mục `frontend/e2e/`) chạy trên trình duyệt thật, đi qua toàn bộ stack: browser → Next.js → DRF → PostgreSQL. Phạm vi là các luồng cốt lõi:

- **Xác thực:** đăng ký → đăng xuất → đăng nhập lại; chặn truy cập khi chưa đăng nhập.
- **Vòng đời công việc:** tạo công việc → xem chi tiết → danh sách → đổi trạng thái Mới → Đang xử lý → Hoàn thành.
- **Sửa/xoá công việc:** sửa tiêu đề (lưu và hiển thị lại) → xoá (qua hộp thoại xác nhận).
- **Tìm kiếm & lọc:** tìm theo tiêu đề; lọc theo độ ưu tiên / trạng thái.

### Chạy cục bộ

Cần backend + database chạy sẵn ở `http://localhost:8000`:

```bash
# từ thư mục gốc repo — dựng db + backend
docker compose up -d db backend

# lần đầu: cài deps và trình duyệt cho Playwright
cd frontend
npm install
npx playwright install chromium

# chạy test (Playwright tự khởi động `next dev` ở cổng 3000)
npm run test:e2e
```

Nếu frontend đã chạy sẵn, Playwright sẽ tái sử dụng server đó (`reuseExistingServer`).

Vì phân quyền (§5) chỉ cho admin/leader tạo công việc, các test cần một tài khoản admin. `global-setup.ts` tự seed tài khoản này bằng lệnh `manage.py seed_e2e` chạy trong container backend (chọn theo cổng API publish). Lệnh **từ chối chạy khi `DEBUG=False`** để tránh vô tình tạo admin trên production.

Biến môi trường: `NEXT_PUBLIC_API_URL` (mặc định `http://localhost:8000`), `E2E_BASE_URL` (mặc định `http://localhost:3000`); ghi đè tài khoản admin qua `E2E_ADMIN_USERNAME` / `E2E_ADMIN_PASSWORD` / `E2E_ADMIN_EMAIL`.

### CI

Job `e2e` trong `.github/workflows/ci.yml` (sau job `test`) dùng lại Postgres service như job pytest: migrate → `seed_e2e` → chạy backend → `npm ci` → cài Chromium → `playwright test`. Dưới CI, `global-setup.ts` bỏ qua bước seed qua Docker (đã có step seed riêng trong workflow).

## 9. Tiêu chí hoàn thành (Definition of Done)

- [ ] CRUD đầy đủ cho Phòng ban, Nhóm, User và Task (Nhân viên ∈ Nhóm ∈ Phòng ban).
- [ ] Giao việc cho cá nhân / nhóm / phòng ban; giao cho nhóm/phòng → thông báo tới leader đơn vị.
- [ ] Phân quyền cơ bản theo 3 role hoạt động đúng.
- [ ] Trạng thái task chuyển đúng vòng đời; **hệ thống tự động** chuyển `overdue` qua job định kỳ.
- [ ] Dashboard thống kê theo trạng thái / người phụ trách / nhóm / phòng ban.
- [ ] Phân trang + tìm kiếm + lọc.
- [ ] Swagger/OpenAPI mô tả đầy đủ endpoint.
- [ ] `docker compose up` chạy được toàn bộ hệ thống.
- [ ] (Điểm cộng) Gửi email khi giao việc; biểu đồ thống kê.

---
*Tài liệu kỹ thuật ngắn gọn cho dự án học tập cá nhân — Internal Task Management Project.*
