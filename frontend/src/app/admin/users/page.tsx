"use client";

import { Search, X } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button, buttonStyles } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/Modal";
import { apiErrorMessage } from "@/lib/api";
import { useDeleteUser } from "@/lib/admin";
import { cn } from "@/lib/cn";
import { useProfile } from "@/lib/hooks";
import { ROLE_LABELS, userDisplayName } from "@/lib/labels";
import { useDepartments, useTeams, useUsers } from "@/lib/org";
import { User } from "@/lib/types";

const controlClass =
  "rounded-ctrl border border-line-strong bg-card px-2.5 py-1.5 text-sm text-ink outline-none transition focus:border-ink focus:ring-4 focus:ring-line";

export default function AdminUsersPage() {
  const { data: users, isPending } = useUsers(true);
  const { data: teams } = useTeams(true);
  const { data: departments } = useDepartments(true);
  const { data: profile } = useProfile();
  const deleteUser = useDeleteUser();

  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("");
  const [teamFilter, setTeamFilter] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // Team options narrow to the chosen department; membership carries only team
  // ids, so a department filter maps through the teams list to their ids.
  const teamOptions = (teams ?? []).filter(
    (t) => !deptFilter || String(t.department) === deptFilter,
  );
  const deptTeamIds = deptFilter
    ? (teams ?? [])
        .filter((t) => String(t.department) === deptFilter)
        .map((t) => t.id)
    : null;

  const query = search.trim().toLowerCase();
  const shown = (users ?? []).filter((user) => {
    if (
      query &&
      !`${userDisplayName(user)} ${user.email} ${user.username}`
        .toLowerCase()
        .includes(query)
    ) {
      return false;
    }
    if (teamFilter) {
      return user.memberships.some((m) => String(m.team) === teamFilter);
    }
    if (deptTeamIds) {
      return user.memberships.some((m) => deptTeamIds.includes(m.team));
    }
    return true;
  });

  const hasActiveFilters = !!(search || deptFilter || teamFilter);

  function clearFilters() {
    setSearch("");
    setDeptFilter("");
    setTeamFilter("");
  }

  function confirmDelete() {
    if (!deleteTarget) return;
    setDeleteError(null);
    deleteUser.mutate(deleteTarget.id, {
      onSuccess: () => setDeleteTarget(null),
      onError: (err) =>
        setDeleteError(apiErrorMessage(err, "Không xoá được người dùng.")),
    });
  }

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-muted">Người dùng</h2>

      <div className="flex w-full flex-wrap items-center gap-2">
        <div className="relative min-w-[12rem] flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm theo tên, email…"
            className={cn(controlClass, "w-full pl-9")}
          />
        </div>
        <select
          value={deptFilter}
          onChange={(e) => {
            setDeptFilter(e.target.value);
            setTeamFilter("");
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
        <select
          value={teamFilter}
          onChange={(e) => setTeamFilter(e.target.value)}
          className={controlClass}
          aria-label="Lọc theo nhóm"
        >
          <option value="">Mọi nhóm</option>
          {teamOptions.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
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
      ) : !users || users.length === 0 ? (
        <Card className="py-12 text-center text-sm text-muted">
          Chưa có người dùng nào.
        </Card>
      ) : shown.length === 0 ? (
        <Card className="py-12 text-center text-sm text-muted">
          Không có người dùng phù hợp bộ lọc.
        </Card>
      ) : (
        <Card className="divide-y divide-line overflow-hidden">
          {shown.map((user) => (
            <div
              key={user.id}
              className="flex items-start justify-between gap-3 px-4 py-3"
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-ink">
                    {userDisplayName(user)}
                  </span>
                  {user.is_admin && <Badge>Admin</Badge>}
                  <span className="text-sm text-muted">{user.email}</span>
                </div>
                {user.memberships.length > 0 && (
                  <p className="mt-1 text-xs text-faint">
                    {user.memberships
                      .map((m) => `${m.team_name} (${ROLE_LABELS[m.role]})`)
                      .join(" · ")}
                  </p>
                )}
              </div>
              {profile && user.id !== profile.id && !user.is_admin && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => {
                    setDeleteError(null);
                    setDeleteTarget(user);
                  }}
                >
                  Xoá
                </Button>
              )}
            </div>
          ))}
        </Card>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Xoá người dùng"
        message={`Xoá người dùng "${deleteTarget ? userDisplayName(deleteTarget) : ""}"? Hành động này không thể hoàn tác.`}
        loading={deleteUser.isPending}
        error={deleteError}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
