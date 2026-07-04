"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import Header from "@/components/Header";
import TaskForm from "@/components/TaskForm";
import { apiErrorMessage } from "@/lib/api";
import { useRequireAuth } from "@/lib/hooks";
import { useCreateTask } from "@/lib/tasks";
import { TaskPayload } from "@/lib/types";

export default function NewTaskPage() {
  useRequireAuth();
  const router = useRouter();
  const createTask = useCreateTask();
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(payload: TaskPayload) {
    setError(null);
    createTask.mutate(payload, {
      onSuccess: (task) => router.replace(`/tasks/${task.id}`),
      onError: (err) =>
        setError(apiErrorMessage(err, "Không tạo được công việc. Vui lòng thử lại.")),
    });
  }

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-2xl px-4 py-6">
        <h1 className="text-lg font-semibold">Tạo công việc</h1>
        <div className="mt-4 rounded-xl border border-zinc-200 p-6 dark:border-zinc-800">
          <TaskForm
            submitLabel="Tạo công việc"
            submitting={createTask.isPending}
            error={error}
            onSubmit={handleSubmit}
          />
        </div>
      </div>
    </main>
  );
}
