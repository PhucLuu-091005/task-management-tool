import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { LinkPayload, TaskLink } from "@/lib/types";

function linksKey(taskId: number) {
  return ["tasks", "links", taskId] as const;
}

export function useLinks(taskId: number) {
  return useQuery<TaskLink[]>({
    queryKey: linksKey(taskId),
    queryFn: async () => (await api.get(`/tasks/${taskId}/links/`)).data,
  });
}

export function useAddLink(taskId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: LinkPayload) =>
      (await api.post(`/tasks/${taskId}/links/`, payload)).data as TaskLink,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: linksKey(taskId) }),
  });
}

export function useDeleteLink(taskId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (linkId: number) => {
      await api.delete(`/tasks/${taskId}/links/${linkId}/`);
      return linkId;
    },
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: linksKey(taskId) }),
  });
}
