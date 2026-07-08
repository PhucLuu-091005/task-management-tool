"use client";

import { useQueryClient } from "@tanstack/react-query";
import { ChevronDown, LogOut, UserRound } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Avatar } from "@/components/ui/Avatar";
import { useAuth } from "@/lib/auth-context";
import { useProfile } from "@/lib/hooks";
import { userDisplayName } from "@/lib/labels";

export default function AccountMenu() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { signOut } = useAuth();
  const { data: user } = useProfile();

  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  async function handleLogout() {
    setOpen(false);
    await signOut();
    // Drop cached data so the next login can't flash the previous user's profile.
    queryClient.clear();
    router.replace("/login");
  }

  if (!user) return null;

  const itemClass =
    "flex w-full items-center gap-2.5 px-3 py-2 text-sm text-ink transition-colors hover:bg-line/60";

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label="Menu tài khoản"
        className="flex items-center gap-2.5 rounded-full py-1 pl-1 pr-1.5 transition-colors hover:bg-line/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-2 focus-visible:ring-offset-background sm:pr-2.5"
      >
        <Avatar
          src={user.avatar}
          lastName={user.last_name}
          firstName={user.first_name}
          className="h-7 w-7"
          textClassName="text-[11px]"
        />
        <span className="hidden text-sm text-muted sm:inline">
          {userDisplayName(user)}
        </span>
        <ChevronDown
          className="hidden h-4 w-4 text-faint sm:block"
          strokeWidth={1.75}
        />
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 top-full z-40 mt-1.5 w-48 overflow-hidden rounded-ctrl border border-line bg-card py-1 shadow-soft"
        >
          <Link
            href="/account"
            role="menuitem"
            onClick={() => setOpen(false)}
            className={itemClass}
          >
            <UserRound className="h-4 w-4 text-muted" strokeWidth={1.75} />
            Tài khoản
          </Link>
          <button
            type="button"
            role="menuitem"
            onClick={handleLogout}
            className={itemClass}
          >
            <LogOut className="h-4 w-4 text-muted" strokeWidth={1.75} />
            Đăng xuất
          </button>
        </div>
      )}
    </div>
  );
}
