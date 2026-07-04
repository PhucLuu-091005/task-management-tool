# Frontend — Next.js

Giao diện web của hệ thống quản lý công việc nội bộ: **Next.js 14 (App Router) + TypeScript + Tailwind CSS + axios + React Query**.

## Chạy dev (host)

```bash
npm install
npm run dev        # http://localhost:3000
```

Backend phải chạy sẵn (mặc định `http://localhost:8000`). Đổi địa chỉ API bằng cách copy `.env.example` → `.env.local` và sửa `NEXT_PUBLIC_API_URL`.

## Chạy bằng Docker

Từ thư mục gốc của repo:

```bash
docker compose up --build frontend
```

## Cấu trúc

```
src/
├── app/
│   ├── page.tsx           # Trang chủ (yêu cầu đăng nhập): hồ sơ + nhóm
│   ├── login/page.tsx     # Đăng nhập
│   ├── register/page.tsx  # Đăng ký
│   ├── providers.tsx      # React Query provider
│   └── layout.tsx
└── lib/
    ├── api.ts             # axios client + tự refresh JWT khi 401
    ├── auth.ts            # login / register / logout
    ├── auth-storage.ts    # lưu access/refresh token (localStorage)
    ├── hooks.ts           # useProfile
    └── types.ts
```

## Xác thực

Đăng nhập qua `POST /api/users/login/` (SimpleJWT). Access token gắn vào header `Authorization: Bearer …`; khi API trả 401, client tự gọi `POST /api/users/token/refresh` một lần rồi thử lại; refresh hỏng thì xoá token và quay về `/login`. Token lưu ở `localStorage` — chấp nhận cho dự án học tập, production nên cân nhắc cookie `HttpOnly`.

## Lệnh khác

```bash
npm run build      # build production + type-check
npm run lint       # ESLint
```
