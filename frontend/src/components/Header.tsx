"use client";

import { Activity } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import AccountMenu from "@/components/AccountMenu";
import { cn } from "@/lib/cn";
import { useProfile } from "@/lib/hooks";

const NAV_ITEMS = [
  { href: "/tasks", label: "Công việc" },
  { href: "/dashboard", label: "Dashboard" },
];

export default function Header() {
  const pathname = usePathname();
  const { data: user } = useProfile();

  const navItems = user?.is_admin
    ? [...NAV_ITEMS, { href: "/admin", label: "Quản trị" }]
    : NAV_ITEMS;

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
            {navItems.map((item) => {
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
        <AccountMenu />
      </div>
    </header>
  );
}
