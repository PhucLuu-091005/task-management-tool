"use client";

import { ArrowLeft, Pencil, Trash2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import Header from "@/components/Header";
import TaskForm from "@/components/TaskForm";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { apiErrorMessage } from "@/lib/api";
import { assigneeLabel, formatDateTime } from "@/lib/labels";
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
        <Link
          href="/tasks"
          className="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
        >
          <ArrowLeft className="h-4 w-4" strokeWidth={1.75} />
          Công việc
        </Link>

        {isPending ? (
          <Card className="py-12 text-center text-sm text-muted">Đang tải…</Card>
        ) : isError || !task ? (
          <Card className="py-12 text-center text-sm text-muted">
            Không tìm thấy công việc.
          </Card>
        ) : (
          <>
            <div className="flex items-start justify-between gap-3">
              <div>
                <h1 className="text-lg font-semibold tracking-tight">
                  {task.title}
                </h1>
                <p className="mt-1 text-sm text-muted">
                  {assigneeLabel(task)} · Người tạo: {task.created_by_name}
                </p>
              </div>
              <StatusBadge status={task.status} />
            </div>

            {editing ? (
              <Card className="p-6">
                <TaskForm
                  initial={task}
                  submitLabel="Lưu thay đổi"
                  submitting={updateTask.isPending}
                  error={error}
                  onSubmit={handleUpdate}
                />
                <button
                  onClick={() => setEditing(false)}
                  className="mt-3 text-sm text-muted underline underline-offset-2 hover:text-ink"
                >
                  Huỷ
                </button>
              </Card>
            ) : (
              <>
                <Card className="p-6 text-sm">
                  <dl className="grid gap-x-8 gap-y-3 sm:grid-cols-2">
                    <div>
                      <dt className="text-muted">Hạn hoàn thành</dt>
                      <dd className="mt-1 font-medium">
                        {formatDateTime(task.due_date)}
                        {task.is_overdue && (
                          <span className="ml-2 rounded-md bg-status-overbg px-1.5 py-0.5 text-xs font-medium text-status-over">
                            Trễ hạn
                          </span>
                        )}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-muted">Ngày tạo</dt>
                      <dd className="mt-1 font-medium">
                        {formatDateTime(task.created_at)}
                      </dd>
                    </div>
                  </dl>
                  {task.description && (
                    <div className="mt-5 border-t border-line pt-4">
                      <dt className="text-muted">Mô tả</dt>
                      <p className="mt-1.5 whitespace-pre-wrap">
                        {task.description}
                      </p>
                    </div>
                  )}
                </Card>

                {error && <p className="text-sm text-status-over">{error}</p>}

                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setError(null);
                      setEditing(true);
                    }}
                  >
                    <Pencil className="h-4 w-4" strokeWidth={1.75} />
                    Chỉnh sửa
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={handleDelete}
                    disabled={deleteTask.isPending}
                  >
                    <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                    Xoá
                  </Button>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </main>
  );
}
