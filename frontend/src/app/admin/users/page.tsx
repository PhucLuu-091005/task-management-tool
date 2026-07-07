"use client";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { ROLE_LABELS, userDisplayName } from "@/lib/labels";
import { useUsers } from "@/lib/org";

export default function AdminUsersPage() {
  const { data: users, isPending } = useUsers(true);

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-muted">Người dùng</h2>

      {isPending ? (
        <Card className="py-12 text-center text-sm text-muted">Đang tải…</Card>
      ) : !users || users.length === 0 ? (
        <Card className="py-12 text-center text-sm text-muted">
          Chưa có người dùng nào.
        </Card>
      ) : (
        <Card className="divide-y divide-line overflow-hidden">
          {users.map((user) => (
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
