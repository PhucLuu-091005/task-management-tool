"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import TaskForm from "@/components/TaskForm";
import { Modal } from "@/components/ui/Modal";
import { apiErrorMessage } from "@/lib/api";
import { useCreateTask } from "@/lib/tasks";
import { TaskPayload } from "@/lib/types";

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

  // TaskForm remounts (fields reset) each open, but this error lives on the
  // always-mounted modal, so clear it so a prior failure doesn't linger.
  useEffect(() => {
    if (open) setError(null);
  }, [open]);

  function handleSubmit(payload: TaskPayload) {
    setError(null);
    createTask.mutate(payload, {
      onSuccess: (task) => router.push(`/tasks/${task.id}`),
      onError: (err) =>
        setError(
          apiErrorMessage(err, "Không tạo được công việc. Vui lòng thử lại."),
        ),
    });
  }

  return (
    <Modal open={open} onClose={onClose} title="Tạo công việc">
      <TaskForm
        submitLabel="Tạo công việc"
        submitting={createTask.isPending}
        error={error}
        onSubmit={handleSubmit}
      />
    </Modal>
  );
}
