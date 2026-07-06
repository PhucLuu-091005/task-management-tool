"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Activity, LogOut } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { buttonStyles } from "@/components/ui/Button";
import { cn } from "@/lib/cn";
import { useAuth } from "@/lib/auth-context";
import { useProfile } from "@/lib/hooks";

const NAV_ITEMS = [
  { href: "/tasks", label: "Công việc" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/account", label: "Tài khoản" },
];

function initials(last?: string, first?: string): string {
  const a = (last ?? "").trim().charAt(0);
  const b = (first ?? "").trim().charAt(0);
  return (a + b).toUpperCase() || "?";
}

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const { signOut } = useAuth();
  const { data: user } = useProfile();

  async function handleLogout() {
    await signOut();
    // Drop cached data so the next login can't flash the previous user's profile.
    queryClient.clear();
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <div className="flex items-center gap-6">
          <Link href="/tasks" className="flex items-center gap-2.5">
            <span className="grid h-7 w-7 place-items-center rounded-lg bg-ink text-white">
              <Activity className="h-4 w-4" strokeWidth={2} />
            </span>
            <span className="text-[15px] font-semibold tracking-tight">Chốt</span>
          </Link>
          <nav className="hidden items-center gap-1 text-sm sm:flex">
            {NAV_ITEMS.map((item) => {
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "rounded-md px-2.5 py-1.5 transition-colors",
                    active
                      ? "bg-line font-medium text-ink"
                      : "text-muted hover:text-ink",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {user && (
            <div className="hidden items-center gap-2.5 sm:flex">
              <span className="text-sm text-muted">
                {user.last_name} {user.first_name}
              </span>
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-line text-[11px] font-semibold text-ink-soft">
                {initials(user.last_name, user.first_name)}
              </span>
            </div>
          )}
          <button
            onClick={handleLogout}
            className={buttonStyles("ghost", "sm")}
            aria-label="Đăng xuất"
          >
            <LogOut className="h-4 w-4" strokeWidth={1.75} />
            <span className="hidden sm:inline">Đăng xuất</span>
          </button>
        </div>
      </div>
    </header>
  );
}
