"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import Header from "@/components/Header";
import {
  STATUS_BADGE_CLASSES,
  STATUS_LABELS,
  assigneeLabel,
  formatDateTime,
  priorityLabel,
} from "@/lib/labels";
import { useRequireAuth } from "@/lib/hooks";
import { useTasks, useUpdateTaskStatus } from "@/lib/tasks";
import { Task, TaskStatus } from "@/lib/types";

const PAGE_SIZE = 20;

const selectClass =
  "rounded-md border border-zinc-300 bg-transparent px-2 py-1.5 text-sm outline-none focus:border-zinc-500 dark:border-zinc-700";

function StatusControl({ task }: { task: Task }) {
  const updateStatus = useUpdateTaskStatus();

  return (
    <select
      value={task.status}
      disabled={updateStatus.isPending}
      onChange={(e) =>
        updateStatus.mutate({ id: task.id, status: e.target.value as TaskStatus })
      }
      onClick={(e) => e.stopPropagation()}
      className={selectClass}
      aria-label={`Trạng thái: ${task.title}`}
    >
      <option value="new">Mới</option>
      <option value="in_progress">Đang xử lý</option>
      <option value="done">Hoàn thành</option>
      {task.status === "overdue" && (
        <option value="overdue" disabled>
          Quá hạn
        </option>
      )}
    </select>
  );
}

export default function TasksPage() {
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");

  const { data, isPending, isError } = useTasks({ page, search, status, priority });
  useRequireAuth(isError);

  const totalPages = data ? Math.max(1, Math.ceil(data.count / PAGE_SIZE)) : 1;

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    setSearch(searchInput.trim());
    setPage(1);
  }

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-5xl space-y-4 px-4 py-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-lg font-semibold">Công việc</h1>
          <Link
            href="/tasks/new"
            className="rounded-md bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
          >
            + Tạo công việc
          </Link>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Tìm theo tiêu đề, mô tả…"
              className="w-64 rounded-md border border-zinc-300 bg-transparent px-3 py-1.5 text-sm outline-none focus:border-zinc-500 dark:border-zinc-700"
            />
            <button
              type="submit"
              className="rounded-md border border-zinc-300 px-3 py-1.5 text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
            >
              Tìm
            </button>
          </form>
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className={selectClass}
            aria-label="Lọc theo trạng thái"
          >
            <option value="">Mọi trạng thái</option>
            <option value="new">Mới</option>
            <option value="in_progress">Đang xử lý</option>
            <option value="done">Hoàn thành</option>
            <option value="overdue">Quá hạn</option>
          </select>
          <select
            value={priority}
            onChange={(e) => {
              setPriority(e.target.value);
              setPage(1);
            }}
            className={selectClass}
            aria-label="Lọc theo độ ưu tiên"
          >
            <option value="">Mọi độ ưu tiên</option>
            <option value="low">Thấp</option>
            <option value="medium">Trung bình</option>
            <option value="high">Cao</option>
          </select>
        </div>

        {isPending ? (
          <p className="py-8 text-center text-sm text-zinc-500">Đang tải…</p>
        ) : !data || data.results.length === 0 ? (
          <p className="py-8 text-center text-sm text-zinc-500">
            Không có công việc nào.
          </p>
        ) : (
          <ul className="divide-y divide-zinc-100 rounded-xl border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
            {data.results.map((task) => (
              <li
                key={task.id}
                className="flex flex-wrap items-center gap-3 px-4 py-3"
              >
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/tasks/${task.id}`}
                    className="font-medium hover:underline"
                  >
                    {task.title}
                  </Link>
                  <p className="mt-0.5 text-xs text-zinc-500">
                    {assigneeLabel(task)} · Ưu tiên: {priorityLabel(task.priority)} ·
                    Hạn: {formatDateTime(task.due_date)}
                  </p>
                </div>
                {task.is_overdue && task.status !== "overdue" && (
                  <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">
                    Trễ hạn
                  </span>
                )}
                <span
                  className={`rounded px-1.5 py-0.5 text-xs font-medium ${STATUS_BADGE_CLASSES[task.status]}`}
                >
                  {STATUS_LABELS[task.status]}
                </span>
                <StatusControl task={task} />
              </li>
            ))}
          </ul>
        )}

        {data && data.count > 0 && (
          <div className="flex items-center justify-between text-sm text-zinc-500">
            <span>
              {data.count} công việc · Trang {page}/{totalPages}
            </span>
            <div className="flex gap-2">
              <button
                disabled={!data.previous}
                onClick={() => setPage((p) => p - 1)}
                className="rounded-md border border-zinc-300 px-3 py-1.5 disabled:opacity-40 dark:border-zinc-700"
              >
                ← Trước
              </button>
              <button
                disabled={!data.next}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-md border border-zinc-300 px-3 py-1.5 disabled:opacity-40 dark:border-zinc-700"
              >
                Sau →
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
