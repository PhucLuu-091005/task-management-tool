"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { hasSession } from "@/lib/auth-storage";
import { logout } from "@/lib/auth";
import { useProfile } from "@/lib/hooks";

export default function HomePage() {
  const router = useRouter();
  const { data: user, isPending, isError } = useProfile();

  useEffect(() => {
    // isError also covers the case where the refresh flow failed and tokens were cleared.
    if (!hasSession() || isError) router.replace("/login");
  }, [router, isError]);

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  if (isPending || isError || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-zinc-500">Đang tải…</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      <header className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <h1 className="text-base font-semibold">Quản lý công việc nội bộ</h1>
          <div className="flex items-center gap-3">
            <span className="text-sm text-zinc-500">
              {user.last_name} {user.first_name}
            </span>
            <button
              onClick={handleLogout}
              className="rounded-md border border-zinc-300 px-3 py-1.5 text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
            >
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-4xl space-y-6 px-4 py-8">
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

        <p className="text-sm text-zinc-400">
          Danh sách công việc sẽ có ở bước tiếp theo (Epic I2).
        </p>
      </div>
    </main>
  );
}
