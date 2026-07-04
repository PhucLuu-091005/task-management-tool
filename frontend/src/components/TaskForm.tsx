"use client";

import { FormEvent, useState } from "react";

import { useDepartments, useTeams, useUsers } from "@/lib/org";
import { useProfile } from "@/lib/hooks";
import { AssigneeType, Task, TaskPayload } from "@/lib/types";

const inputClass =
  "mt-1 w-full rounded-md border border-zinc-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-zinc-500 dark:border-zinc-700";

// datetime-local wants "YYYY-MM-DDTHH:mm" in local time.
function toInputValue(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

interface TaskFormProps {
  initial?: Task;
  submitLabel: string;
  submitting: boolean;
  error: string | null;
  onSubmit: (payload: TaskPayload) => void;
}

export default function TaskForm({
  initial,
  submitLabel,
  submitting,
  error,
  onSubmit,
}: TaskFormProps) {
  const { data: me } = useProfile();
  const isAdmin = me?.is_admin ?? false;
  const { data: users } = useUsers(isAdmin);
  const { data: teams } = useTeams(isAdmin);
  const { data: departments } = useDepartments(isAdmin);

  const [title, setTitle] = useState(initial?.title ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [priority, setPriority] = useState(initial?.priority ?? "");
  const [dueDate, setDueDate] = useState(toInputValue(initial?.due_date ?? null));
  const [assigneeType, setAssigneeType] = useState<AssigneeType>(
    initial?.assignee_type ?? "user",
  );
  const [assigneeUser, setAssigneeUser] = useState(
    initial?.assignee_user?.toString() ?? "",
  );
  const [assigneeTeam, setAssigneeTeam] = useState(
    initial?.assignee_team?.toString() ?? "",
  );
  const [assigneeDepartment, setAssigneeDepartment] = useState(
    initial?.assignee_department?.toString() ?? "",
  );

  // Non-admins can't list users/teams/departments; offer themselves and their
  // teams, plus the task's current assignee so editing never forces a reassignment.
  function seedInitial(
    choices: { id: number; label: string }[],
    id: number | null | undefined,
    label: string | null | undefined,
  ) {
    if (!id || choices.some((c) => c.id === id)) return choices;
    return [{ id, label: label ?? `#${id}` }, ...choices];
  }

  const userChoices = seedInitial(
    isAdmin
      ? (users ?? []).map((u) => ({
          id: u.id,
          label: `${u.last_name} ${u.first_name}`.trim() || u.username,
        }))
      : me
        ? [
            {
              id: me.id,
              label: `${me.last_name} ${me.first_name}`.trim() || me.username,
            },
          ]
        : [],
    initial?.assignee_user,
    initial?.assignee_user_name,
  );
  const teamChoices = seedInitial(
    isAdmin
      ? (teams ?? []).map((t) => ({ id: t.id, label: t.name }))
      : (me?.memberships ?? []).map((m) => ({ id: m.team, label: m.team_name })),
    initial?.assignee_team,
    initial?.assignee_team_name,
  );
  const departmentChoices = seedInitial(
    isAdmin ? (departments ?? []).map((d) => ({ id: d.id, label: d.name })) : [],
    initial?.assignee_department,
    initial?.assignee_department_name,
  );

  const typeChoices: { value: AssigneeType; label: string }[] = [
    { value: "user", label: "Cá nhân" },
    { value: "team", label: "Nhóm" },
    ...(departmentChoices.length > 0
      ? [{ value: "department" as const, label: "Phòng ban" }]
      : []),
  ];

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit({
      title,
      description,
      priority,
      due_date: dueDate ? new Date(dueDate).toISOString() : null,
      assignee_type: assigneeType,
      assignee_user:
        assigneeType === "user" && assigneeUser ? Number(assigneeUser) : null,
      assignee_team:
        assigneeType === "team" && assigneeTeam ? Number(assigneeTeam) : null,
      assignee_department:
        assigneeType === "department" && assigneeDepartment
          ? Number(assigneeDepartment)
          : null,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium">
          Tiêu đề
        </label>
        <input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={200}
          className={inputClass}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium">
          Mô tả
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className={inputClass}
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="priority" className="block text-sm font-medium">
            Độ ưu tiên
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as typeof priority)}
            className={inputClass}
          >
            <option value="">—</option>
            <option value="low">Thấp</option>
            <option value="medium">Trung bình</option>
            <option value="high">Cao</option>
          </select>
        </div>
        <div>
          <label htmlFor="due_date" className="block text-sm font-medium">
            Hạn hoàn thành
          </label>
          <input
            id="due_date"
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className={inputClass}
          />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="assignee_type" className="block text-sm font-medium">
            Giao cho
          </label>
          <select
            id="assignee_type"
            value={assigneeType}
            onChange={(e) => setAssigneeType(e.target.value as AssigneeType)}
            className={inputClass}
          >
            {typeChoices.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          {assigneeType === "user" && (
            <>
              <label htmlFor="assignee_user" className="block text-sm font-medium">
                Cá nhân
              </label>
              <select
                id="assignee_user"
                value={assigneeUser}
                onChange={(e) => setAssigneeUser(e.target.value)}
                required
                className={inputClass}
              >
                <option value="">— Chọn người —</option>
                {userChoices.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
            </>
          )}
          {assigneeType === "team" && (
            <>
              <label htmlFor="assignee_team" className="block text-sm font-medium">
                Nhóm
              </label>
              <select
                id="assignee_team"
                value={assigneeTeam}
                onChange={(e) => setAssigneeTeam(e.target.value)}
                required
                className={inputClass}
              >
                <option value="">— Chọn nhóm —</option>
                {teamChoices.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
            </>
          )}
          {assigneeType === "department" && (
            <>
              <label
                htmlFor="assignee_department"
                className="block text-sm font-medium"
              >
                Phòng ban
              </label>
              <select
                id="assignee_department"
                value={assigneeDepartment}
                onChange={(e) => setAssigneeDepartment(e.target.value)}
                required
                className={inputClass}
              >
                <option value="">— Chọn phòng ban —</option>
                {departmentChoices.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
            </>
          )}
        </div>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
      >
        {submitting ? "Đang lưu…" : submitLabel}
      </button>
    </form>
  );
}
