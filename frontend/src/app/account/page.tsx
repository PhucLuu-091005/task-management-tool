"use client";

import Header from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useProfile, useRequireAuth } from "@/lib/hooks";

export default function AccountPage() {
  const { data: user, isPending, isError, error } = useProfile();
  useRequireAuth(error);

  if (isError) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-status-over">
          Không tải được thông tin tài khoản. Vui lòng thử lại.
        </p>
      </main>
    );
  }

  if (isPending || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted">Đang tải…</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      <Header />

      <div className="mx-auto max-w-5xl space-y-6 px-4 py-8">
        <h1 className="text-lg font-semibold tracking-tight">Tài khoản</h1>

        <Card className="p-6">
          <h2 className="text-[13px] font-medium uppercase tracking-wide text-faint">
            Thông tin
          </h2>
          <dl className="mt-4 grid gap-x-8 gap-y-3 text-sm sm:grid-cols-2">
            <div className="flex justify-between sm:block">
              <dt className="text-muted">Họ tên</dt>
              <dd className="mt-0 font-medium sm:mt-1">
                {user.last_name} {user.first_name}
                {user.is_admin && <Badge className="ml-2">Admin</Badge>}
              </dd>
            </div>
            <div className="flex justify-between sm:block">
              <dt className="text-muted">Tên đăng nhập</dt>
              <dd className="mt-0 font-medium sm:mt-1">{user.username}</dd>
            </div>
            <div className="flex justify-between sm:block">
              <dt className="text-muted">Email</dt>
              <dd className="mt-0 font-medium sm:mt-1">{user.email}</dd>
            </div>
          </dl>
        </Card>

        <Card className="p-6">
          <h2 className="text-[13px] font-medium uppercase tracking-wide text-faint">
            Nhóm của tôi
          </h2>
          {user.memberships.length === 0 ? (
            <p className="mt-4 text-sm text-muted">Bạn chưa thuộc nhóm nào.</p>
          ) : (
            <ul className="mt-4 divide-y divide-line overflow-hidden rounded-ctrl border border-line">
              {user.memberships.map((m) => (
                <li
                  key={m.team}
                  className="flex items-center justify-between px-3.5 py-2.5 text-sm"
                >
                  <span className="font-medium">{m.team_name}</span>
                  <span className="text-xs text-muted">
                    {m.role === "leader" ? "Trưởng nhóm" : "Thành viên"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </main>
  );
}
