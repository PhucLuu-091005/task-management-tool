import { Role, Task, TaskPriority, TaskStatus, User } from "@/lib/types";

export const STATUS_LABELS: Record<TaskStatus, string> = {
  new: "Mới",
  in_progress: "Đang xử lý",
  done: "Hoàn thành",
  overdue: "Quá hạn",
};

export const STATUS_BADGE_CLASSES: Record<TaskStatus, string> = {
  new: "bg-status-newbg text-status-new",
  in_progress: "bg-status-progbg text-status-prog",
  done: "bg-status-donebg text-status-done",
  overdue: "bg-status-overbg text-status-over",
};

// Manual status machine, mirroring the backend's ALLOWED_TRANSITIONS. `overdue`
// is system-set (the flip job), never a manual target, so it's absent as a value.
export const ALLOWED_NEXT_STATUS: Record<TaskStatus, TaskStatus[]> = {
  new: ["in_progress"],
  in_progress: ["done"],
  done: [],
  overdue: ["in_progress", "done"],
};

export const PRIORITY_LABELS: Record<Exclude<TaskPriority, "">, string> = {
  low: "Thấp",
  medium: "Trung bình",
  high: "Cao",
};

export function priorityLabel(priority: TaskPriority): string {
  return priority ? PRIORITY_LABELS[priority] : "—";
}

export const ROLE_LABELS: Record<Role, string> = {
  leader: "Trưởng nhóm",
  member: "Thành viên",
};

// Vietnamese name order (family name first), falling back to the username.
export function userDisplayName(
  user: Pick<User, "first_name" | "last_name" | "username">,
): string {
  return `${user.last_name} ${user.first_name}`.trim() || user.username;
}

export function assigneeLabel(task: Task): string {
  switch (task.assignee_type) {
    case "user":
      return task.assignee_user_name ?? "—";
    case "team":
      return task.assignee_team_name ? `Nhóm ${task.assignee_team_name}` : "—";
    case "department":
      return task.assignee_department_name
        ? `Phòng ${task.assignee_department_name}`
        : "—";
  }
}

export function formatDateTime(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}
