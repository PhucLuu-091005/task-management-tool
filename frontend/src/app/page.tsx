"use client";

import Header from "@/components/Header";
import { useProfile, useRequireAuth } from "@/lib/hooks";

export default function HomePage() {
  const { data: user, isPending, isError } = useProfile();
  useRequireAuth(isError);

  if (isPending || isError || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-zinc-500">Đang tải…</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      <Header />

      <div className="mx-auto max-w-5xl space-y-6 px-4 py-8">
        <section className="rounded-xl border border-zinc-200 p-6 dark:border-zinc-800">
          <h2 className="text-sm font-medium text-zinc-500">Tài khoản</h2>
          <dl className="mt-3 grid gap-x-8 gap-y-2 text-sm sm:grid-cols-2">
            <div className="flex justify-between sm:block">
              <dt className="text-zinc-500">Họ tên</dt>
              <dd className="font-medium">
                {user.last_name} {user.first_name}
                {user.is_admin && (
                  <span className="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                    Admin
                  </span>
                )}
              </dd>
            </div>
            <div className="flex justify-between sm:block">
              <dt className="text-zinc-500">Tên đăng nhập</dt>
              <dd className="font-medium">{user.username}</dd>
            </div>
            <div className="flex justify-between sm:block">
              <dt className="text-zinc-500">Email</dt>
              <dd className="font-medium">{user.email}</dd>
            </div>
          </dl>
        </section>

        <section className="rounded-xl border border-zinc-200 p-6 dark:border-zinc-800">
          <h2 className="text-sm font-medium text-zinc-500">Nhóm của tôi</h2>
          {user.memberships.length === 0 ? (
            <p className="mt-3 text-sm text-zinc-500">
              Bạn chưa thuộc nhóm nào.
            </p>
          ) : (
            <ul className="mt-3 space-y-2 text-sm">
              {user.memberships.map((m) => (
                <li
                  key={m.team}
                  className="flex items-center justify-between rounded-md border border-zinc-100 px-3 py-2 dark:border-zinc-800"
                >
                  <span className="font-medium">{m.team_name}</span>
                  <span className="text-xs text-zinc-500">
                    {m.role === "leader" ? "Trưởng nhóm" : "Thành viên"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
