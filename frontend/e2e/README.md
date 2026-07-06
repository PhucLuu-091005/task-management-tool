# E2E tests (Playwright)

Browser tests covering the core happy path: **register → create task → drive its status lifecycle**.
Each test self-registers a fresh account, so no seed data is required.

## Chạy

Cần backend + database chạy sẵn ở `http://localhost:8000`:

```bash
# từ thư mục gốc repo — dựng db + backend
docker compose up -d db backend

# lần đầu: cài deps và browser cho Playwright
cd frontend
npm install
npx playwright install chromium

# chạy test (Playwright tự khởi động `next dev` ở cổng 3000)
npm run test:e2e
```

Nếu frontend đã chạy sẵn, Playwright sẽ tái sử dụng server đó (`reuseExistingServer`).

## Biến môi trường

- `NEXT_PUBLIC_API_URL` — URL của Django API (mặc định `http://localhost:8000`).
- `E2E_BASE_URL` — URL của web app (mặc định `http://localhost:3000`).

## CI

Chạy tự động trong job `e2e` của `.github/workflows/ci.yml` (sau job `test`):
migrate → `manage.py seed_e2e` → chạy backend → `npm ci` → cài Chromium → `playwright test`.
Dưới CI, `global-setup.ts` bỏ qua bước seed qua Docker (đã có step seed riêng trong workflow).

## Phạm vi

- `auth.spec.ts` — đăng ký, đăng xuất, đăng nhập lại; chặn truy cập khi chưa đăng nhập.
- `task-lifecycle.spec.ts` — tạo công việc giao cho chính mình, đổi trạng thái Mới → Đang xử lý → Hoàn thành.
