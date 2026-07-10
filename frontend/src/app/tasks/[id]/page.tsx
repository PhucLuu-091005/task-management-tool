"use client";

import { ArrowLeft, Pencil, Trash2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import Header from "@/components/Header";
import StatusMenu from "@/components/StatusMenu";
import TaskAttachments from "@/components/TaskAttachments";
import TaskForm from "@/components/TaskForm";
import TaskLinks from "@/components/TaskLinks";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/Modal";
import { apiErrorMessage } from "@/lib/api";
import { assigneeLabel, formatDateTime, priorityLabel } from "@/lib/labels";
import { useProfile, useRequireAuth } from "@/lib/hooks";
import { useDeleteTask, useTask, useUpdateTask } from "@/lib/tasks";
import { Task, TaskPayload } from "@/lib/types";

function MetaRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="shrink-0 text-muted">{label}</dt>
      <dd className="text-right font-medium">{children}</dd>
    </div>
  );
}

function InfoCard({ task }: { task: Task }) {
  return (
    <Card className="p-6 text-sm">
      <div className="flex items-center justify-between gap-3 border-b border-line pb-4">
        <span className="text-muted">Trạng thái</span>
        <StatusMenu task={task} />
      </div>
      <dl className="mt-4 space-y-3">
        <MetaRow label="Người nhận">{assigneeLabel(task)}</MetaRow>
        <MetaRow label="Người tạo">{task.created_by_name}</MetaRow>
        <MetaRow label="Độ ưu tiên">{priorityLabel(task.priority)}</MetaRow>
        <MetaRow label="Hạn hoàn thành">
          <span className="inline-flex flex-wrap items-center justify-end gap-x-2 gap-y-1">
            <span className="whitespace-nowrap">{formatDateTime(task.due_date)}</span>
            {task.is_overdue && (
              <span className="whitespace-nowrap rounded-md bg-status-overbg px-1.5 py-0.5 text-xs font-medium text-status-over">
                Trễ hạn
              </span>
            )}
          </span>
        </MetaRow>
        <MetaRow label="Giao lúc">{formatDateTime(task.assigned_at)}</MetaRow>
        {task.started_at && (
          <MetaRow label="Bắt đầu">{formatDateTime(task.started_at)}</MetaRow>
        )}
        {task.completed_at && (
          <MetaRow label="Hoàn thành">
            {formatDateTime(task.completed_at)}
          </MetaRow>
        )}
        <MetaRow label="Ngày tạo">{formatDateTime(task.created_at)}</MetaRow>
      </dl>
    </Card>
  );
}

export default function TaskDetailPage() {
  const params = useParams<{ id: string }>();
  const taskId = Number(params.id);
  const router = useRouter();

  const { data: task, isPending, isError } = useTask(taskId);
  const { data: profile } = useProfile();
  useRequireAuth();
  const updateTask = useUpdateTask(taskId);
  const deleteTask = useDeleteTask();

  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // UX-only heuristic for showing delete controls; the backend still enforces
  // that only the uploader or a task editor may remove an attachment/link.
  const canManageItem = (addedBy: number | null) =>
    !!profile &&
    (profile.is_admin ||
      addedBy === profile.id ||
      task?.created_by === profile.id);

  function handleUpdate(payload: TaskPayload) {
    setError(null);
    updateTask.mutate(payload, {
      onSuccess: () => setEditing(false),
      onError: (err) =>
        setError(apiErrorMessage(err, "Không cập nhật được công việc.")),
    });
  }

  async function handleDelete() {
    setDeleteError(null);
    try {
      await deleteTask.mutateAsync(taskId);
      router.replace("/tasks");
    } catch (err) {
      setDeleteError(
        apiErrorMessage(err, "Bạn không có quyền xoá công việc này."),
      );
    }
  }

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-5xl space-y-4 px-4 py-6">
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
        ) : editing ? (
          <Card className="max-w-2xl p-6">
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
            <div className="flex flex-wrap items-start justify-between gap-3">
              <h1 className="text-lg font-semibold tracking-tight">
                {task.title}
              </h1>
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
                  onClick={() => {
                    setDeleteError(null);
                    setConfirmingDelete(true);
                  }}
                  disabled={deleteTask.isPending}
                >
                  <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                  Xoá
                </Button>
              </div>
            </div>

            {error && <p className="text-sm text-status-over">{error}</p>}

            <div className="grid gap-4 lg:grid-cols-3">
              <div className="space-y-4 lg:col-span-2">
                <Card className="p-6">
                  <h2 className="text-sm font-semibold tracking-tight">Mô tả</h2>
                  {task.description ? (
                    <p className="mt-3 whitespace-pre-wrap text-sm text-ink">
                      {task.description}
                    </p>
                  ) : (
                    <p className="mt-3 text-sm text-muted">Chưa có mô tả.</p>
                  )}
                </Card>
                <TaskAttachments taskId={task.id} canManage={canManageItem} />
                <TaskLinks taskId={task.id} canManage={canManageItem} />
              </div>

              <aside className="lg:col-span-1">
                <InfoCard task={task} />
              </aside>
            </div>

            <ConfirmDialog
              open={confirmingDelete}
              title="Xoá công việc"
              message={`Xoá công việc "${task.title}"? Hành động này không thể hoàn tác.`}
              loading={deleteTask.isPending}
              error={deleteError}
              onConfirm={handleDelete}
              onCancel={() => setConfirmingDelete(false)}
            />
          </>
        )}
      </div>
    </main>
  );
}
