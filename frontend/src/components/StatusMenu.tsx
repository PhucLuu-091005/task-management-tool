"use client";

import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { ConfirmDialog } from "@/components/ui/Modal";
import { apiErrorMessage } from "@/lib/api";
import { cn } from "@/lib/cn";
import {
  ALLOWED_NEXT_STATUS,
  STATUS_BADGE_CLASSES,
  STATUS_LABELS,
} from "@/lib/labels";
import { useUpdateTaskStatus } from "@/lib/tasks";
import { Task, TaskStatus } from "@/lib/types";

const pill =
  "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium transition";

// A single status control: the colored status pill IS the trigger. Clicking it
// opens the allowed transitions; a terminal status (no transitions) renders as a
// plain, non-interactive badge. The lifecycle is one-way, so a picked transition
// is confirmed before it's applied — a misclick shouldn't be unrecoverable.
export default function StatusMenu({
  task,
  align = "end",
}: {
  task: Task;
  align?: "start" | "end";
}) {
  const updateStatus = useUpdateTaskStatus();
  const [open, setOpen] = useState(false);
  // The menu renders inline, so an ancestor's overflow clips it: at the bottom of
  // a list it must open upward instead of down. Decided from viewport space on open.
  const [placement, setPlacement] = useState<"down" | "up">("down");
  const [pending, setPending] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const ref = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const next = ALLOWED_NEXT_STATUS[task.status];
  const locked = next.length === 0;

  function toggle() {
    if (open) {
      setOpen(false);
      return;
    }
    const trigger = triggerRef.current;
    if (trigger) {
      const rect = trigger.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      // Rough menu height: one row per option (~2rem) plus the wrapper padding.
      const estimatedHeight = next.length * 32 + 16;
      setPlacement(spaceBelow < estimatedHeight ? "up" : "down");
    }
    setOpen(true);
  }

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

  function pick(status: TaskStatus) {
    setOpen(false);
    setError(null);
    setPending(status);
  }

  function confirmChange() {
    if (!pending) return;
    updateStatus.mutate(
      { id: task.id, status: pending },
      {
        onSuccess: () => setPending(null),
        onError: (err) =>
          setError(apiErrorMessage(err, "Không đổi được trạng thái.")),
      },
    );
  }

  if (locked) {
    return (
      <span className={cn(pill, STATUS_BADGE_CLASSES[task.status])}>
        {STATUS_LABELS[task.status]}
      </span>
    );
  }

  return (
    <div ref={ref} className="relative flex flex-col items-end gap-1">
      <button
        ref={triggerRef}
        type="button"
        disabled={updateStatus.isPending}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label="Đổi trạng thái"
        onClick={(e) => {
          e.stopPropagation();
          e.preventDefault();
          toggle();
        }}
        className={cn(
          pill,
          STATUS_BADGE_CLASSES[task.status],
          "cursor-pointer hover:brightness-95",
          updateStatus.isPending && "opacity-70",
        )}
      >
        {STATUS_LABELS[task.status]}
        <ChevronDown className="h-3 w-3 opacity-70" strokeWidth={2.5} />
      </button>

      {open && (
        <div
          role="menu"
          className={cn(
            "absolute z-40 min-w-[9rem] overflow-hidden rounded-ctrl border border-line bg-card py-1 shadow-soft",
            placement === "up" ? "bottom-full mb-1" : "top-full mt-1",
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
                pick(s);
              }}
              className="flex w-full items-center px-3 py-1.5 text-left text-sm text-ink transition-colors hover:bg-line/60"
            >
              {STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={pending !== null}
        title="Đổi trạng thái"
        message={`Chuyển trạng thái từ "${STATUS_LABELS[task.status]}" sang "${pending ? STATUS_LABELS[pending] : ""}"? Trạng thái không thể hoàn tác.`}
        confirmLabel="Chuyển"
        loading={updateStatus.isPending}
        error={error}
        onConfirm={confirmChange}
        onCancel={() => {
          setPending(null);
          setError(null);
        }}
      />
    </div>
  );
}
