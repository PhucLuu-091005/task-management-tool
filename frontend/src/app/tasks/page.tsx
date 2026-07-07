"use client";

import { ChevronLeft, ChevronRight, Plus, Search } from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";

import CreateTaskModal from "@/components/CreateTaskModal";
import Header from "@/components/Header";
import { StatusBadge } from "@/components/ui/Badge";
import { buttonStyles } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { apiErrorMessage } from "@/lib/api";
import { cn } from "@/lib/cn";
import {
  assigneeLabel,
  formatDateTime,
  priorityLabel,
  userDisplayName,
} from "@/lib/labels";
import { useProfile, useRequireAuth } from "@/lib/hooks";
import { useDepartments, useTeams, useUsers } from "@/lib/org";
import { useTasks, useUpdateTaskStatus } from "@/lib/tasks";
import { Task, TaskStatus } from "@/lib/types";

const controlClass =
  "rounded-ctrl border border-line-strong bg-card px-2.5 py-1.5 text-sm text-ink outline-none transition focus:border-ink focus:ring-4 focus:ring-line";

function StatusControl({ task }: { task: Task }) {
  const updateStatus = useUpdateTaskStatus();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="flex flex-col items-end gap-1">
      <select
        value={task.status}
        disabled={updateStatus.isPending}
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
        onClick={(e) => e.stopPropagation()}
        className={controlClass}
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
      {error && (
        <span className="max-w-[12rem] text-right text-xs text-status-over">
          {error}
        </span>
      )}
    </div>
  );
}

export default function TasksPage() {
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");
  const [assigneeType, setAssigneeType] = useState("");
  const [assigneeId, setAssigneeId] = useState("");
  const [creating, setCreating] = useState(false);

  // Auth is guarded by session presence only — a failing list fetch is a data
  // error to render in place, not a reason to bounce the user to /login.
  useRequireAuth();
  const { data: profile } = useProfile();
  // Assignee choice lists are admin-only; non-admins only see status/priority/
  // search. Each list loads only once its assignee type is selected.
  const isAdmin = !!profile?.is_admin;
  const { data: users } = useUsers(isAdmin && assigneeType === "user");
  const { data: teams } = useTeams(isAdmin && assigneeType === "team");
  const { data: departments } = useDepartments(
    isAdmin && assigneeType === "department",
  );

  function resetAssigneeType(next: string) {
    setAssigneeType(next);
    setAssigneeId("");
    setPage(1);
  }

  const { data, isPending, isError } = useTasks({
    page,
    search,
    status,
    priority,
    assigneeType,
    assigneeUser: assigneeType === "user" ? assigneeId : "",
    team: assigneeType === "team" ? assigneeId : "",
    department: assigneeType === "department" ? assigneeId : "",
  });

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    setSearch(searchInput.trim());
    setPage(1);
  }

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-5xl space-y-5 px-4 py-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-lg font-semibold tracking-tight">Công việc</h1>
          <button
            type="button"
            onClick={() => setCreating(true)}
            className={buttonStyles("primary", "md")}
          >
            <Plus className="h-4 w-4" strokeWidth={2} />
            Tạo công việc
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <form onSubmit={handleSearch} className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint" />
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Tìm theo tiêu đề, mô tả…"
              className={cn(controlClass, "w-64 pl-9")}
            />
          </form>
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className={controlClass}
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
            className={controlClass}
            aria-label="Lọc theo độ ưu tiên"
          >
            <option value="">Mọi độ ưu tiên</option>
            <option value="low">Thấp</option>
            <option value="medium">Trung bình</option>
            <option value="high">Cao</option>
          </select>

          {isAdmin && (
            <>
              <select
                value={assigneeType}
                onChange={(e) => resetAssigneeType(e.target.value)}
                className={controlClass}
                aria-label="Lọc theo loại người nhận"
              >
                <option value="">Mọi người nhận</option>
                <option value="user">Người</option>
                <option value="team">Nhóm</option>
                <option value="department">Phòng ban</option>
              </select>

              {assigneeType === "user" && (
                <select
                  value={assigneeId}
                  onChange={(e) => {
                    setAssigneeId(e.target.value);
                    setPage(1);
                  }}
                  className={controlClass}
                  aria-label="Lọc theo người"
                >
                  <option value="">Mọi người</option>
                  {users?.map((u) => (
                    <option key={u.id} value={u.id}>
                      {userDisplayName(u)}
                    </option>
                  ))}
                </select>
              )}
              {assigneeType === "team" && (
                <select
                  value={assigneeId}
                  onChange={(e) => {
                    setAssigneeId(e.target.value);
                    setPage(1);
                  }}
                  className={controlClass}
                  aria-label="Lọc theo nhóm"
                >
                  <option value="">Mọi nhóm</option>
                  {teams?.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
              )}
              {assigneeType === "department" && (
                <select
                  value={assigneeId}
                  onChange={(e) => {
                    setAssigneeId(e.target.value);
                    setPage(1);
                  }}
                  className={controlClass}
                  aria-label="Lọc theo phòng ban"
                >
                  <option value="">Mọi phòng ban</option>
                  {departments?.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </select>
              )}
            </>
          )}
        </div>

        {isPending ? (
          <Card className="py-12 text-center text-sm text-muted">Đang tải…</Card>
        ) : isError ? (
          <Card className="py-12 text-center text-sm text-status-over">
            Không tải được danh sách công việc. Vui lòng thử lại.
          </Card>
        ) : !data || data.results.length === 0 ? (
          <Card className="py-12 text-center text-sm text-muted">
            Không có công việc nào.
          </Card>
        ) : (
          <Card className="divide-y divide-line overflow-hidden">
            {data.results.map((task) => (
              <div
                key={task.id}
                className="flex flex-wrap items-center gap-3 px-4 py-3"
              >
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/tasks/${task.id}`}
                    className="font-medium text-ink hover:underline"
                  >
                    {task.title}
                  </Link>
                  <p className="mt-0.5 text-xs text-faint">
                    {assigneeLabel(task)} · Ưu tiên: {priorityLabel(task.priority)}{" "}
                    · Hạn: {formatDateTime(task.due_date)}
                  </p>
                </div>
                {task.is_overdue && task.status !== "overdue" && (
                  <span className="rounded-md bg-status-overbg px-1.5 py-0.5 text-xs font-medium text-status-over">
                    Trễ hạn
                  </span>
                )}
                <StatusBadge status={task.status} />
                <StatusControl task={task} />
              </div>
            ))}
          </Card>
        )}

        {data && data.count > 0 && (
          <div className="flex items-center justify-between text-sm text-muted">
            <span>
              {data.count} công việc · Trang {page}
            </span>
            <div className="flex gap-2">
              <button
                disabled={!data.previous}
                onClick={() => setPage((p) => p - 1)}
                className={buttonStyles("secondary", "sm")}
              >
                <ChevronLeft className="h-4 w-4" strokeWidth={1.75} />
                Trước
              </button>
              <button
                disabled={!data.next}
                onClick={() => setPage((p) => p + 1)}
                className={buttonStyles("secondary", "sm")}
              >
                Sau
                <ChevronRight className="h-4 w-4" strokeWidth={1.75} />
              </button>
            </div>
          </div>
        )}

        <CreateTaskModal
          open={creating}
          onClose={() => setCreating(false)}
        />
      </div>
    </main>
  );
}
