"use client";

import { Plus, Search, X } from "lucide-react";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import CreateTaskModal from "@/components/CreateTaskModal";
import Header from "@/components/Header";
import StatusMenu from "@/components/StatusMenu";
import { buttonStyles } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Pagination } from "@/components/ui/Pagination";
import { Tooltip } from "@/components/ui/Tooltip";
import { cn } from "@/lib/cn";
import {
  assigneeLabel,
  formatDateTime,
  priorityLabel,
  userDisplayName,
} from "@/lib/labels";
import { useProfile, useRequireAuth } from "@/lib/hooks";
import { useDepartments, useTeams, useUsers } from "@/lib/org";
import { TASKS_PAGE_SIZE, useTasks } from "@/lib/tasks";

const controlClass =
  "rounded-ctrl border border-line-strong bg-card px-2.5 py-1.5 text-sm text-ink outline-none transition focus:border-ink focus:ring-4 focus:ring-line";

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
  const isAdmin = !!profile?.is_admin;
  // Only *deny* once the profile has loaded and says so; while it's loading keep
  // the button active (the backend still enforces) so an admin/leader sees no
  // flash of a disabled control.
  const denyCreate = !!profile && !profile.can_create_tasks;
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

  const hasActiveFilters = !!(search || status || priority || assigneeType);

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    setSearch(searchInput.trim());
    setPage(1);
  }

  function clearFilters() {
    setSearchInput("");
    setSearch("");
    setStatus("");
    setPriority("");
    setAssigneeType("");
    setAssigneeId("");
    setPage(1);
  }

  const totalPages = data ? Math.ceil(data.count / TASKS_PAGE_SIZE) : 0;

  // If a filter or status change shrinks the results below the current page, step
  // back so we never request an out-of-range page (which 404s → the error card).
  useEffect(() => {
    if (data && page > 1 && page > totalPages) setPage(Math.max(totalPages, 1));
  }, [data, page, totalPages]);

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-5xl space-y-5 px-4 py-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-lg font-semibold tracking-tight">Công việc</h1>
          {denyCreate ? (
            <Tooltip label="Chỉ admin, trưởng nhóm hoặc trưởng phòng mới được tạo công việc.">
              <button
                type="button"
                disabled
                className={buttonStyles("primary", "md")}
              >
                <Plus className="h-4 w-4" strokeWidth={2} />
                Tạo công việc
              </button>
            </Tooltip>
          ) : (
            <button
              type="button"
              onClick={() => setCreating(true)}
              className={buttonStyles("primary", "md")}
            >
              <Plus className="h-4 w-4" strokeWidth={2} />
              Tạo công việc
            </button>
          )}
        </div>

        <div className="flex w-full flex-wrap items-center gap-2">
          <form onSubmit={handleSearch} className="relative min-w-[12rem] flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint" />
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Tìm theo tiêu đề, mô tả…"
              className={cn(controlClass, "w-full pl-9")}
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

          <button
            type="button"
            onClick={clearFilters}
            disabled={!hasActiveFilters}
            className={cn(buttonStyles("ghost", "sm"), "ml-auto")}
          >
            <X className="h-4 w-4" strokeWidth={1.75} />
            Xoá bộ lọc
          </button>
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
          <Card className="divide-y divide-line">
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
                  <span className="whitespace-nowrap rounded-md bg-status-overbg px-1.5 py-0.5 text-xs font-medium text-status-over">
                    Trễ hạn
                  </span>
                )}
                <StatusMenu task={task} />
              </div>
            ))}
          </Card>
        )}

        {data && data.count > 0 && (
          <div className="flex flex-col items-center gap-2">
            <Pagination page={page} total={totalPages} onChange={setPage} />
            <p className="text-xs text-muted">
              {data.count} công việc · Trang {page}/{totalPages}
            </p>
          </div>
        )}

        {!denyCreate && (
          <CreateTaskModal open={creating} onClose={() => setCreating(false)} />
        )}
      </div>
    </main>
  );
}
