"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import Header from "@/components/Header";
import TaskForm from "@/components/TaskForm";
import { Card } from "@/components/ui/Card";
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
        setError(
          apiErrorMessage(err, "Không tạo được công việc. Vui lòng thử lại."),
        ),
    });
  }

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto max-w-2xl px-4 py-6">
        <Link
          href="/tasks"
          className="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
        >
          <ArrowLeft className="h-4 w-4" strokeWidth={1.75} />
          Công việc
        </Link>
        <h1 className="mt-3 text-lg font-semibold tracking-tight">
          Tạo công việc
        </h1>
        <Card className="mt-4 p-6">
          <TaskForm
            submitLabel="Tạo công việc"
            submitting={createTask.isPending}
            error={error}
            onSubmit={handleSubmit}
          />
        </Card>
      </div>
    </main>
  );
}
