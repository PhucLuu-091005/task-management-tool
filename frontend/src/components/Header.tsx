"use client";

import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { logout } from "@/lib/auth";
import { useProfile } from "@/lib/hooks";

const NAV_ITEMS = [
  { href: "/tasks", label: "Công việc" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/", label: "Tài khoản" },
];

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const { data: user } = useProfile();

  async function handleLogout() {
    await logout();
    // Drop cached data so the next login can't flash the previous user's profile.
    queryClient.clear();
    router.replace("/login");
  }

  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <span className="text-base font-semibold">
            Quản lý công việc nội bộ
          </span>
          <nav className="flex items-center gap-4 text-sm">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={
                  pathname === item.href
                    ? "font-medium"
                    : "text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
                }
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {user && (
            <span className="text-sm text-zinc-500">
              {user.last_name} {user.first_name}
            </span>
          )}
          <button
            onClick={handleLogout}
            className="rounded-md border border-zinc-300 px-3 py-1.5 text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
          >
            Đăng xuất
          </button>
        </div>
      </div>
    </header>
  );
}
