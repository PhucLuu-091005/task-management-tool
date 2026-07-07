"use client";

import { Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Field, fieldInput } from "@/components/ui/Field";
import { apiErrorMessage } from "@/lib/api";
import { useAddMember, useRemoveMember, useUpdateMemberRole } from "@/lib/admin";
import { userDisplayName } from "@/lib/labels";
import { Role, Team, User } from "@/lib/types";

const inlineSelect =
  "rounded-ctrl border border-line-strong bg-card px-2 py-1.5 text-sm text-ink outline-none transition focus:border-ink focus:ring-4 focus:ring-line";

export default function TeamMembersModal({
  team,
  users,
  onClose,
}: {
  team: Team | null;
  users: User[];
  onClose: () => void;
}) {
  const teamId = team?.id ?? 0;
  const addMember = useAddMember(teamId);
  const updateRole = useUpdateMemberRole(teamId);
  const removeMember = useRemoveMember(teamId);

  const [newUser, setNewUser] = useState("");
  const [newRole, setNewRole] = useState<Role>("member");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!team) return;
    setNewUser("");
    setNewRole("member");
    setError(null);
  }, [team]);

  const isMember = (u: User) => u.memberships.some((m) => m.team === teamId);
  const members = team ? users.filter(isMember) : [];
  const candidates = team ? users.filter((u) => !isMember(u)) : [];
  const roleOf = (u: User): Role =>
    u.memberships.find((m) => m.team === teamId)?.role ?? "member";

  function handleAdd(e: FormEvent) {
    e.preventDefault();
    if (!newUser) return;
    setError(null);
    addMember.mutate(
      { user: Number(newUser), role: newRole },
      {
        onSuccess: () => setNewUser(""),
        onError: (err) =>
          setError(apiErrorMessage(err, "Không thêm được thành viên.")),
      },
    );
  }

  return (
    <Modal
      open={!!team}
      onClose={onClose}
      title={team ? `Thành viên · ${team.name}` : ""}
    >
      <div className="space-y-4">
        {members.length === 0 ? (
          <p className="text-sm text-muted">Chưa có thành viên.</p>
        ) : (
          <ul className="divide-y divide-line">
            {members.map((u) => (
              <li key={u.id} className="flex items-center gap-3 py-2.5">
                <span className="min-w-0 flex-1 truncate text-sm">
                  {userDisplayName(u)}
                </span>
                <select
                  value={roleOf(u)}
                  disabled={updateRole.isPending}
                  onChange={(e) => {
                    setError(null);
                    updateRole.mutate(
                      { userId: u.id, role: e.target.value as Role },
                      {
                        onError: (err) =>
                          setError(
                            apiErrorMessage(err, "Không đổi được vai trò."),
                          ),
                      },
                    );
                  }}
                  className={inlineSelect}
                  aria-label={`Vai trò của ${userDisplayName(u)}`}
                >
                  <option value="member">Thành viên</option>
                  <option value="leader">Trưởng nhóm</option>
                </select>
                <button
                  type="button"
                  onClick={() => {
                    setError(null);
                    removeMember.mutate(u.id, {
                      onError: (err) =>
                        setError(
                          apiErrorMessage(err, "Không xoá được thành viên."),
                        ),
                    });
                  }}
                  disabled={removeMember.isPending}
                  className="text-faint transition-colors hover:text-status-over disabled:opacity-50"
                  aria-label={`Xoá ${userDisplayName(u)}`}
                >
                  <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                </button>
              </li>
            ))}
          </ul>
        )}

        <form
          onSubmit={handleAdd}
          className="flex items-end gap-2 border-t border-line pt-4"
        >
          <Field label="Thêm thành viên" htmlFor="add-member" className="flex-1">
            <select
              id="add-member"
              value={newUser}
              onChange={(e) => setNewUser(e.target.value)}
              className={fieldInput}
            >
              <option value="">Chọn người…</option>
              {candidates.map((u) => (
                <option key={u.id} value={u.id}>
                  {userDisplayName(u)}
                </option>
              ))}
            </select>
          </Field>
          <select
            value={newRole}
            onChange={(e) => setNewRole(e.target.value as Role)}
            className={inlineSelect}
            aria-label="Vai trò thành viên mới"
          >
            <option value="member">Thành viên</option>
            <option value="leader">Trưởng nhóm</option>
          </select>
          <Button type="submit" size="sm" disabled={!newUser || addMember.isPending}>
            <Plus className="h-4 w-4" strokeWidth={2} />
            Thêm
          </Button>
        </form>

        {error && <p className="text-sm text-status-over">{error}</p>}
      </div>
    </Modal>
  );
}
