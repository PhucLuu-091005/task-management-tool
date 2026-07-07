"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import Header from "@/components/Header";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";
import { useRequireAdmin } from "@/lib/hooks";

const TABS = [
  { href: "/admin/teams", label: "Nhóm" },
  { href: "/admin/departments", label: "Phòng ban" },
  { href: "/admin/users", label: "Người dùng" },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { checking, isAdmin } = useRequireAdmin();
  const pathname = usePathname();

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-5xl space-y-5 px-4 py-6">
        {checking || !isAdmin ? (
          <Card className="py-12 text-center text-sm text-muted">Đang tải…</Card>
        ) : (
          <>
            <h1 className="text-lg font-semibold tracking-tight">Quản trị</h1>
            <nav className="flex gap-1 border-b border-line">
              {TABS.map((tab) => {
                const active = pathname.startsWith(tab.href);
                return (
                  <Link
                    key={tab.href}
                    href={tab.href}
                    className={cn(
                      "-mb-px border-b-2 px-3 py-2 text-sm transition-colors",
                      active
                        ? "border-ink font-medium text-ink"
                        : "border-transparent text-muted hover:text-ink",
                    )}
                  >
                    {tab.label}
                  </Link>
                );
              })}
            </nav>
            {children}
          </>
        )}
      </div>
    </main>
  );
}
