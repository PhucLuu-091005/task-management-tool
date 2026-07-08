"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { ROLE_LABELS, userDisplayName } from "@/lib/labels";
import { useDepartments, useTeams, useUsers } from "@/lib/org";

const controlClass =
  "rounded-ctrl border border-line-strong bg-card px-2.5 py-1.5 text-sm text-ink outline-none transition focus:border-ink focus:ring-4 focus:ring-line";

export default function AdminUsersPage() {
  const { data: users, isPending } = useUsers(true);
  const { data: teams } = useTeams(true);
  const { data: departments } = useDepartments(true);

  const [deptFilter, setDeptFilter] = useState("");
  const [teamFilter, setTeamFilter] = useState("");

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

  const shown = (users ?? []).filter((user) => {
    if (teamFilter) {
      return user.memberships.some((m) => String(m.team) === teamFilter);
    }
    if (deptTeamIds) {
      return user.memberships.some((m) => deptTeamIds.includes(m.team));
    }
    return true;
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-sm font-medium text-muted">Người dùng</h2>
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
            <div key={user.id} className="px-4 py-3">
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
          ))}
        </Card>
      )}
    </div>
  );
}
