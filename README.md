# Internal Task Management — Hệ thống quản lý công việc nội bộ

Ứng dụng web quản lý công việc cho phòng/nhóm: tạo việc, giao việc, theo dõi tiến độ và cập nhật trạng thái. Mục tiêu mô phỏng quy trình quản lý task trong doanh nghiệp, đồng thời là dự án học/thực hành full-stack với **Next.js (React) + Django + PostgreSQL**.

## 1. Tính năng chính

1. **Quản lý danh sách công việc:** thêm, sửa, xoá, tìm kiếm, lọc theo trạng thái.
2. **Giao việc** cho nhân sự phụ trách (assignee).
3. **Cập nhật trạng thái:** Tạo mới → Đang xử lý → Hoàn thành → Quá hạn (tự động đánh dấu quá hạn theo deadline).
4. **Quản lý người dùng theo role:** `admin`, `leader`, `member`.
5. **Dashboard** thống kê số lượng công việc theo trạng thái / theo người phụ trách.

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
        │                                          └──► Celery + Redis (email/thông báo - tùy chọn)
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

### User (mở rộng từ Django `AbstractUser`)
| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| id | int (PK) | |
| username / email | string | email dùng để đăng nhập & gửi thông báo |
| full_name | string | |
| role | enum | `admin` \| `leader` \| `member` |
| is_active | bool | |

### Task
| Trường | Kiểu | Ghi chú |
|--------|------|---------|
| id | int (PK) | |
| title | string | bắt buộc |
| description | text | |
| status | enum | `new` \| `in_progress` \| `done` \| `overdue` |
| priority | enum | `low` \| `medium` \| `high` (tùy chọn) |
| assignee | FK → User | người phụ trách |
| created_by | FK → User | người tạo |
| due_date | datetime | dùng để tính quá hạn |
| created_at / updated_at | datetime | tự động |

> **Quy tắc quá hạn:** task có `due_date < now` và `status != done` sẽ được coi là `overdue` (tính lúc đọc dữ liệu hoặc qua job định kỳ).

## 5. Phân quyền (RBAC)

| Hành động | admin | leader | member |
|-----------|:---:|:---:|:---:|
| Quản lý người dùng (CRUD) | ✅ | ❌ | ❌ |
| Tạo / sửa / xoá mọi task | ✅ | ✅ (trong nhóm) | ❌ |
| Giao việc cho người khác | ✅ | ✅ | ❌ |
| Xem dashboard toàn bộ | ✅ | ✅ | chỉ task của mình |
| Cập nhật trạng thái task được giao | ✅ | ✅ | ✅ |

## 6. API chính (REST)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/auth/login/` | Đăng nhập, trả JWT |
| POST | `/api/auth/refresh/` | Làm mới token |
| GET/POST | `/api/users/` | Danh sách / tạo người dùng (admin) |
| GET/PUT/DELETE | `/api/users/{id}/` | Chi tiết / sửa / xoá người dùng |
| GET/POST | `/api/tasks/` | Danh sách (phân trang, filter, search) / tạo task |
| GET/PUT/PATCH/DELETE | `/api/tasks/{id}/` | Chi tiết / cập nhật / xoá task |
| PATCH | `/api/tasks/{id}/status/` | Cập nhật trạng thái |
| GET | `/api/dashboard/stats/` | Thống kê theo trạng thái / người phụ trách |

Query params cho `/api/tasks/`: `?status=`, `?assignee=`, `?search=`, `?page=`, `?ordering=`.

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

## 9. Tiêu chí hoàn thành (Definition of Done)

- [ ] CRUD đầy đủ cho Task và User.
- [ ] Phân quyền cơ bản theo 3 role hoạt động đúng.
- [ ] Trạng thái task chuyển đúng vòng đời, tự đánh dấu quá hạn.
- [ ] Dashboard thống kê theo trạng thái và người phụ trách.
- [ ] Phân trang + tìm kiếm + lọc.
- [ ] Swagger/OpenAPI mô tả đầy đủ endpoint.
- [ ] `docker compose up` chạy được toàn bộ hệ thống.
- [ ] (Điểm cộng) Gửi email khi giao việc; biểu đồ thống kê.

---
*Tài liệu kỹ thuật ngắn gọn cho dự án học tập cá nhân — Internal Task Management Project.*
