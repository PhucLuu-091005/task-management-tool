"use client";

import { useState } from "react";

import { apiErrorMessage } from "@/lib/api";
import { ALLOWED_NEXT_STATUS, STATUS_LABELS } from "@/lib/labels";
import { useUpdateTaskStatus } from "@/lib/tasks";
import { Task, TaskStatus } from "@/lib/types";

const controlClass =
  "rounded-ctrl border border-line-strong bg-card px-2.5 py-1.5 text-sm text-ink outline-none transition focus:border-ink focus:ring-4 focus:ring-line disabled:opacity-60";

export default function TaskStatusControl({ task }: { task: Task }) {
  const updateStatus = useUpdateTaskStatus();
  const [error, setError] = useState<string | null>(null);

  const nextStatuses = ALLOWED_NEXT_STATUS[task.status];
  const locked = nextStatuses.length === 0;

  return (
    <div className="flex flex-col items-end gap-1">
      <select
        value={task.status}
        disabled={locked || updateStatus.isPending}
        onChange={(e) => {
          setError(null);
          updateStatus.mutate(
            { id: task.id, status: e.target.value as TaskStatus },
            {
              onError: (err) =>
                setError(apiErrorMessage(err, "Không đổi được trạng thái.")),
            },
          );
        }}
        className={controlClass}
        aria-label="Đổi trạng thái"
      >
        <option value={task.status} disabled>
          {STATUS_LABELS[task.status]}
        </option>
        {nextStatuses.map((status) => (
          <option key={status} value={status}>
            {STATUS_LABELS[status]}
          </option>
        ))}
      </select>
      {error && (
        <span className="text-right text-xs text-status-over">{error}</span>
      )}
    </div>
  );
}
