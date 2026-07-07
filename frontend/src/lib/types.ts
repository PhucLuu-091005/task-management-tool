export type Role = "leader" | "member";

export interface TeamMembership {
  team: number;
  team_name: string;
  role: Role;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  memberships: TeamMembership[];
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
}

export type TaskStatus = "new" | "in_progress" | "done" | "overdue";
export type TaskPriority = "" | "low" | "medium" | "high";
export type AssigneeType = "user" | "team" | "department";

export interface Task {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_type: AssigneeType;
  assignee_user: number | null;
  assignee_user_name: string | null;
  assignee_team: number | null;
  assignee_team_name: string | null;
  assignee_department: number | null;
  assignee_department_name: string | null;
  created_by: number;
  created_by_name: string;
  due_date: string | null;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskPayload {
  title: string;
  description: string;
  priority: TaskPriority;
  due_date: string | null;
  assignee_type: AssigneeType;
  assignee_user: number | null;
  assignee_team: number | null;
  assignee_department: number | null;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Team {
  id: number;
  name: string;
  department: number;
  description: string;
}

export interface TeamPayload {
  name: string;
  department: number;
  description: string;
}

export interface Department {
  id: number;
  name: string;
  description: string;
  lead: number | null;
}

export interface DepartmentPayload {
  name: string;
  description: string;
  lead: number | null;
}

export interface TeamMemberPayload {
  user: number;
  role: Role;
}
