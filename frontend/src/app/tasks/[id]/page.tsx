"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import Header from "@/components/Header";
import TaskForm from "@/components/TaskForm";
import { apiErrorMessage } from "@/lib/api";
import {
  STATUS_BADGE_CLASSES,
  STATUS_LABELS,
  assigneeLabel,
  formatDateTime,
} from "@/lib/labels";
import { useRequireAuth } from "@/lib/hooks";
import { useDeleteTask, useTask, useUpdateTask } from "@/lib/tasks";
import { TaskPayload } from "@/lib/types";

export default function TaskDetailPage() {
  const params = useParams<{ id: string }>();
  const taskId = Number(params.id);
  const router = useRouter();

  const { data: task, isPending, isError } = useTask(taskId);
  useRequireAuth();
  const updateTask = useUpdateTask(taskId);
  const deleteTask = useDeleteTask();

  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleUpdate(payload: TaskPayload) {
    setError(null);
    updateTask.mutate(payload, {
      onSuccess: () => setEditing(false),
      onError: (err) =>
        setError(apiErrorMessage(err, "Không cập nhật được công việc.")),
    });
  }

  async function handleDelete() {
    if (!confirm("Xoá công việc này?")) return;
    try {
      await deleteTask.mutateAsync(taskId);
      router.replace("/tasks");
    } catch (err) {
      setError(apiErrorMessage(err, "Bạn không có quyền xoá công việc này."));
    }
  }

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-2xl space-y-4 px-4 py-6">
        {isPending ? (
          <p className="py-8 text-center text-sm text-zinc-500">Đang tải…</p>
        ) : isError || !task ? (
          <p className="py-8 text-center text-sm text-zinc-500">
            Không tìm thấy công việc.
          </p>
        ) : (
          <>
            <div className="flex items-start justify-between gap-3">
              <div>
                <h1 className="text-lg font-semibold">{task.title}</h1>
                <p className="mt-1 text-sm text-zinc-500">
                  {assigneeLabel(task)} · Người tạo: {task.created_by_name}
                </p>
              </div>
              <span
                className={`rounded px-2 py-1 text-xs font-medium ${STATUS_BADGE_CLASSES[task.status]}`}
              >
                {STATUS_LABELS[task.status]}
              </span>
            </div>

            {editing ? (
              <div className="rounded-xl border border-zinc-200 p-6 dark:border-zinc-800">
                <TaskForm
                  initial={task}
                  submitLabel="Lưu thay đổi"
                  submitting={updateTask.isPending}
                  error={error}
                  onSubmit={handleUpdate}
                />
                <button
                  onClick={() => setEditing(false)}
                  className="mt-3 text-sm text-zinc-500 underline"
                >
                  Huỷ
                </button>
              </div>
            ) : (
              <>
                <div className="rounded-xl border border-zinc-200 p-6 text-sm dark:border-zinc-800">
                  <dl className="grid gap-x-8 gap-y-2 sm:grid-cols-2">
                    <div>
                      <dt className="text-zinc-500">Hạn hoàn thành</dt>
                      <dd className="font-medium">
                        {formatDateTime(task.due_date)}
                        {task.is_overdue && (
                          <span className="ml-2 rounded bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">
                            Trễ hạn
                          </span>
                        )}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-zinc-500">Ngày tạo</dt>
                      <dd className="font-medium">{formatDateTime(task.created_at)}</dd>
                    </div>
                  </dl>
                  {task.description && (
                    <div className="mt-4">
                      <dt className="text-sm text-zinc-500">Mô tả</dt>
                      <p className="mt-1 whitespace-pre-wrap">{task.description}</p>
                    </div>
                  )}
                </div>

                {error && <p className="text-sm text-red-600">{error}</p>}

                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setError(null);
                      setEditing(true);
                    }}
                    className="rounded-md border border-zinc-300 px-3 py-1.5 text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800"
                  >
                    Chỉnh sửa
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={deleteTask.isPending}
                    className="rounded-md border border-red-300 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50 disabled:opacity-50 dark:border-red-900 dark:text-red-400 dark:hover:bg-red-950"
                  >
                    Xoá
                  </button>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </main>
  );
}
