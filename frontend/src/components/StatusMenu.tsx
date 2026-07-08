"use client";

import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { apiErrorMessage } from "@/lib/api";
import { cn } from "@/lib/cn";
import {
  ALLOWED_NEXT_STATUS,
  STATUS_BADGE_CLASSES,
  STATUS_LABELS,
} from "@/lib/labels";
import { useUpdateTaskStatus } from "@/lib/tasks";
import { Task, TaskStatus } from "@/lib/types";

// A single status control: the colored status pill IS the trigger. Clicking it
// opens the allowed transitions; a terminal status (no transitions) renders as a
// plain, non-interactive badge. Replaces the old badge + separate dropdown.
export default function StatusMenu({
  task,
  align = "end",
}: {
  task: Task;
  align?: "start" | "end";
}) {
  const updateStatus = useUpdateTaskStatus();
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  const next = ALLOWED_NEXT_STATUS[task.status];
  const locked = next.length === 0;

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

  function choose(status: TaskStatus) {
    setOpen(false);
    setError(null);
    updateStatus.mutate(
      { id: task.id, status },
      { onError: (err) => setError(apiErrorMessage(err, "Không đổi được trạng thái.")) },
    );
  }

  const pill =
    "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium transition";

  return (
    <div ref={ref} className="relative flex flex-col items-end gap-1">
      <button
        type="button"
        disabled={locked || updateStatus.isPending}
        aria-haspopup={locked ? undefined : "menu"}
        aria-expanded={locked ? undefined : open}
        aria-label={locked ? undefined : "Đổi trạng thái"}
        onClick={(e) => {
          e.stopPropagation();
          e.preventDefault();
          setOpen((v) => !v);
        }}
        className={cn(
          pill,
          STATUS_BADGE_CLASSES[task.status],
          locked ? "cursor-default" : "cursor-pointer hover:brightness-95",
          updateStatus.isPending && "opacity-70",
        )}
      >
        {STATUS_LABELS[task.status]}
        {!locked && <ChevronDown className="h-3 w-3 opacity-70" strokeWidth={2.5} />}
      </button>

      {open && !locked && (
        <div
          role="menu"
          className={cn(
            "absolute top-full z-40 mt-1 min-w-[9rem] overflow-hidden rounded-ctrl border border-line bg-card py-1 shadow-soft",
            align === "end" ? "right-0" : "left-0",
          )}
        >
          {next.map((s) => (
            <button
              key={s}
              type="button"
              role="menuitem"
              onClick={(e) => {
                e.stopPropagation();
                choose(s);
              }}
              className="flex w-full items-center px-3 py-1.5 text-left text-sm text-ink transition-colors hover:bg-line/60"
            >
              {STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      )}

      {error && (
        <span className="max-w-[12rem] text-right text-xs text-status-over">
          {error}
        </span>
      )}
    </div>
  );
}
