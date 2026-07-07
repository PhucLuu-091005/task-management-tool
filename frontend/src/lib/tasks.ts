import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { isAxiosError } from "axios";

import { api } from "@/lib/api";
import { Paginated, Task, TaskPayload, TaskStatus } from "@/lib/types";

export interface TaskListParams {
  page: number;
  search: string;
  status: string;
  priority: string;
  assigneeType: string;
  assigneeUser: string;
  team: string;
  department: string;
}

export function useTasks(params: TaskListParams) {
  return useQuery<Paginated<Task>>({
    queryKey: ["tasks", "list", params],
    queryFn: async () => {
      const query: Record<string, string | number> = { page: params.page };
      if (params.search) query.search = params.search;
      if (params.status) query.status = params.status;
      if (params.priority) query.priority = params.priority;
      // A specific assignee narrows more than its type, so it wins; the bare
      // type filter only applies when no concrete assignee is chosen.
      if (params.assigneeUser) query.assignee_user = params.assigneeUser;
      else if (params.team) query.team = params.team;
      else if (params.department) query.department = params.department;
      else if (params.assigneeType) query.assignee_type = params.assigneeType;
      return (await api.get("/tasks/", { params: query })).data;
    },
    placeholderData: keepPreviousData,
  });
}

export function useTask(id: number) {
  return useQuery<Task>({
    queryKey: ["tasks", "detail", id],
    queryFn: async () => (await api.get(`/tasks/${id}/`)).data,
    // 404/403 won't heal on retry; fail fast so "not found" renders promptly.
    retry: (failureCount, error) =>
      !(isAxiosError(error) && error.response) && failureCount < 2,
  });
}

function useInvalidateTasks() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ["tasks"] });
}

export function useCreateTask() {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: async (payload: TaskPayload) =>
      (await api.post("/tasks/", payload)).data as Task,
    onSuccess: invalidate,
  });
}

export function useUpdateTask(id: number) {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: async (payload: Partial<TaskPayload>) =>
      (await api.patch(`/tasks/${id}/`, payload)).data as Task,
    onSuccess: invalidate,
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/tasks/${id}/`);
      return id;
    },
    onSuccess: (id) => {
      // Drop (don't refetch) the deleted detail query: refetching it would 404
      // and stall the awaited invalidation, delaying the caller's redirect.
      queryClient.removeQueries({ queryKey: ["tasks", "detail", id] });
      queryClient.invalidateQueries({ queryKey: ["tasks", "list"] });
    },
  });
}

export function useUpdateTaskStatus() {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: async ({ id, status }: { id: number; status: TaskStatus }) =>
      (await api.patch(`/tasks/${id}/status/`, { status })).data as Task,
    onSuccess: invalidate,
  });
}
