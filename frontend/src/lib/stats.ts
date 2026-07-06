import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { TaskStatus } from "@/lib/types";

export interface TaskStats {
  total: number;
  by_status: Record<TaskStatus, number>;
  by_assignee_user: { assignee_user_id: number; count: number }[];
  by_team: { assignee_team_id: number; count: number }[];
  by_department: { assignee_department_id: number; count: number }[];
}

export function useTaskStats() {
  return useQuery<TaskStats>({
    queryKey: ["tasks", "stats"],
    queryFn: async () => (await api.get("/tasks/stats/")).data,
  });
}
