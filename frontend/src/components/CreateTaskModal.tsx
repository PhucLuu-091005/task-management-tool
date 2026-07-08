"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import CreateTaskExtras, {
  PendingImage,
  PendingLink,
} from "@/components/CreateTaskExtras";
import TaskForm from "@/components/TaskForm";
import { Modal } from "@/components/ui/Modal";
import { api, apiErrorMessage } from "@/lib/api";
import { useCreateTask } from "@/lib/tasks";
import { TaskPayload } from "@/lib/types";

// Best-effort: the task already exists, so attach each independently and let the
// detail page (source of truth) show the result — any item that fails to upload
// can be re-added there rather than blocking the create flow.
async function uploadExtras(
  taskId: number,
  links: PendingLink[],
  images: PendingImage[],
) {
  for (const link of links) {
    try {
      await api.post(`/tasks/${taskId}/links/`, {
        url: link.url,
        label: link.label,
      });
    } catch {
      /* re-addable on the detail page */
    }
  }
  for (const img of images) {
    try {
      const form = new FormData();
      form.append("image", img.file);
      await api.post(`/tasks/${taskId}/attachments/`, form);
    } catch {
      /* re-addable on the detail page */
    }
  }
}

export default function CreateTaskModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const router = useRouter();
  const createTask = useCreateTask();
  const [error, setError] = useState<string | null>(null);
  const [links, setLinks] = useState<PendingLink[]>([]);
  const [images, setImages] = useState<PendingImage[]>([]);
  const [uploading, setUploading] = useState(false);

  // TaskForm remounts (fields reset) each open, but this state lives on the
  // always-mounted modal, so clear it so a prior attempt doesn't linger.
  useEffect(() => {
    if (open) {
      setError(null);
      setLinks([]);
      setImages([]);
      setUploading(false);
    }
  }, [open]);

  function handleSubmit(payload: TaskPayload) {
    setError(null);
    createTask.mutate(payload, {
      onSuccess: async (task) => {
        if (links.length || images.length) {
          setUploading(true);
          await uploadExtras(task.id, links, images);
        }
        router.push(`/tasks/${task.id}`);
      },
      onError: (err) =>
        setError(
          apiErrorMessage(err, "Không tạo được công việc. Vui lòng thử lại."),
        ),
    });
  }

  const submitting = createTask.isPending || uploading;

  return (
    <Modal open={open} onClose={onClose} title="Tạo công việc">
      <TaskForm
        submitLabel="Tạo công việc"
        submitting={submitting}
        error={error}
        onSubmit={handleSubmit}
      >
        <CreateTaskExtras
          links={links}
          onLinksChange={setLinks}
          images={images}
          onImagesChange={setImages}
          disabled={submitting}
        />
      </TaskForm>
    </Modal>
  );
}
