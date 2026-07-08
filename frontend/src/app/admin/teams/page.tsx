"use client";

import { Plus } from "lucide-react";
import { useState } from "react";

import TeamFormModal from "@/components/admin/TeamFormModal";
import TeamMembersModal from "@/components/admin/TeamMembersModal";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/Modal";
import { apiErrorMessage } from "@/lib/api";
import { useDeleteTeam } from "@/lib/admin";
import { useDepartments, useTeams, useUsers } from "@/lib/org";
import { Team } from "@/lib/types";

const controlClass =
  "rounded-ctrl border border-line-strong bg-card px-2.5 py-1.5 text-sm text-ink outline-none transition focus:border-ink focus:ring-4 focus:ring-line";

export default function AdminTeamsPage() {
  const { data: teams, isPending } = useTeams(true);
  const { data: departments } = useDepartments(true);
  const { data: users } = useUsers(true);
  const deleteTeam = useDeleteTeam();

  const [formOpen, setFormOpen] = useState(false);
  const [editTeam, setEditTeam] = useState<Team | null>(null);
  const [membersTeam, setMembersTeam] = useState<Team | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Team | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deptFilter, setDeptFilter] = useState("");

  const shown = (teams ?? []).filter(
    (t) => !deptFilter || String(t.department) === deptFilter,
  );

  const departmentName = (id: number) =>
    departments?.find((d) => d.id === id)?.name ?? "—";
  const memberCount = (teamId: number) =>
    users?.filter((u) => u.memberships.some((m) => m.team === teamId)).length ??
    0;

  function openCreate() {
    setEditTeam(null);
    setFormOpen(true);
  }
  function openEdit(team: Team) {
    setEditTeam(team);
    setFormOpen(true);
  }
  function confirmDelete() {
    if (!deleteTarget) return;
    setDeleteError(null);
    deleteTeam.mutate(deleteTarget.id, {
      onSuccess: () => setDeleteTarget(null),
      onError: (err) =>
        setDeleteError(apiErrorMessage(err, "Không xoá được nhóm.")),
    });
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-medium text-muted">Nhóm</h2>
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
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
        </div>
        <Button size="sm" onClick={openCreate}>
          <Plus className="h-4 w-4" strokeWidth={2} />
          Tạo nhóm
        </Button>
      </div>

      {isPending ? (
        <Card className="py-12 text-center text-sm text-muted">Đang tải…</Card>
      ) : !teams || teams.length === 0 ? (
        <Card className="py-12 text-center text-sm text-muted">
          Chưa có nhóm nào.
        </Card>
      ) : shown.length === 0 ? (
        <Card className="py-12 text-center text-sm text-muted">
          Không có nhóm phù hợp bộ lọc.
        </Card>
      ) : (
        <Card className="divide-y divide-line overflow-hidden">
          {shown.map((team) => (
            <div
              key={team.id}
              className="flex flex-wrap items-center gap-3 px-4 py-3"
            >
              <div className="min-w-0 flex-1">
                <p className="font-medium text-ink">{team.name}</p>
                <p className="mt-0.5 text-xs text-faint">
                  {departmentName(team.department)} · {memberCount(team.id)}{" "}
                  thành viên
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setMembersTeam(team)}
              >
                Thành viên
              </Button>
              <Button variant="secondary" size="sm" onClick={() => openEdit(team)}>
                Sửa
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  setDeleteError(null);
                  setDeleteTarget(team);
                }}
              >
                Xoá
              </Button>
            </div>
          ))}
        </Card>
      )}

      <TeamFormModal
        open={formOpen}
        onClose={() => setFormOpen(false)}
        team={editTeam}
        departments={departments ?? []}
      />
      <TeamMembersModal
        team={membersTeam}
        users={users ?? []}
        onClose={() => setMembersTeam(null)}
      />
      <ConfirmDialog
        open={!!deleteTarget}
        title="Xoá nhóm"
        message={`Xoá nhóm "${deleteTarget?.name}"? Mọi thành viên của nhóm sẽ bị gỡ.`}
        loading={deleteTeam.isPending}
        error={deleteError}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
