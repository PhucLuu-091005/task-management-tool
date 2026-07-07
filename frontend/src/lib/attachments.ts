import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { TaskAttachment } from "@/lib/types";

// Mirror the backend limits (apps/tasks/validators.py) so the UI can reject a
// bad file before wasting an upload round-trip; the backend still enforces them.
export const ATTACHMENT_MAX_BYTES = 5 * 1024 * 1024;
export const ATTACHMENT_ACCEPT = "image/jpeg,image/png,image/gif,image/webp";
const ACCEPTED_TYPES = ATTACHMENT_ACCEPT.split(",");

export function attachmentError(file: File): string | null {
  if (!ACCEPTED_TYPES.includes(file.type)) {
    return "Chỉ chấp nhận ảnh JPEG, PNG, GIF hoặc WEBP.";
  }
  if (file.size > ATTACHMENT_MAX_BYTES) {
    return "Ảnh vượt quá 5MB.";
  }
  return null;
}

function attachmentsKey(taskId: number) {
  return ["tasks", "attachments", taskId] as const;
}

export function useAttachments(taskId: number) {
  return useQuery<TaskAttachment[]>({
    queryKey: attachmentsKey(taskId),
    queryFn: async () => (await api.get(`/tasks/${taskId}/attachments/`)).data,
  });
}

export function useUploadAttachment(taskId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ file, caption }: { file: File; caption: string }) => {
      const form = new FormData();
      form.append("image", file);
      if (caption) form.append("caption", caption);
      return (await api.post(`/tasks/${taskId}/attachments/`, form))
        .data as TaskAttachment;
    },
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: attachmentsKey(taskId) }),
  });
}

export function useDeleteAttachment(taskId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (attachmentId: number) => {
      await api.delete(`/tasks/${taskId}/attachments/${attachmentId}/`);
      return attachmentId;
    },
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: attachmentsKey(taskId) }),
  });
}
