"use client";

import { Plus } from "lucide-react";
import { useState } from "react";

import DepartmentFormModal from "@/components/admin/DepartmentFormModal";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/Modal";
import { apiErrorMessage } from "@/lib/api";
import { useDeleteDepartment } from "@/lib/admin";
import { userDisplayName } from "@/lib/labels";
import { useDepartments, useUsers } from "@/lib/org";
import { Department } from "@/lib/types";

export default function AdminDepartmentsPage() {
  const { data: departments, isPending } = useDepartments(true);
  const { data: users } = useUsers(true);
  const deleteDepartment = useDeleteDepartment();

  const [formOpen, setFormOpen] = useState(false);
  const [editDepartment, setEditDepartment] = useState<Department | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Department | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const leadName = (id: number | null) => {
    if (id == null) return "—";
    const user = users?.find((u) => u.id === id);
    return user ? userDisplayName(user) : "—";
  };

  function openCreate() {
    setEditDepartment(null);
    setFormOpen(true);
  }
  function openEdit(department: Department) {
    setEditDepartment(department);
    setFormOpen(true);
  }
  function confirmDelete() {
    if (!deleteTarget) return;
    setDeleteError(null);
    deleteDepartment.mutate(deleteTarget.id, {
      onSuccess: () => setDeleteTarget(null),
      onError: (err) =>
        setDeleteError(
          apiErrorMessage(
            err,
            "Không xoá được phòng ban. Có thể phòng ban vẫn còn nhóm.",
          ),
        ),
    });
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-medium text-muted">Phòng ban</h2>
        <Button size="sm" onClick={openCreate}>
          <Plus className="h-4 w-4" strokeWidth={2} />
          Tạo phòng ban
        </Button>
      </div>

      {isPending ? (
        <Card className="py-12 text-center text-sm text-muted">Đang tải…</Card>
      ) : !departments || departments.length === 0 ? (
        <Card className="py-12 text-center text-sm text-muted">
          Chưa có phòng ban nào.
        </Card>
      ) : (
        <Card className="divide-y divide-line overflow-hidden">
          {departments.map((department) => (
            <div
              key={department.id}
              className="flex flex-wrap items-center gap-3 px-4 py-3"
            >
              <div className="min-w-0 flex-1">
                <p className="font-medium text-ink">{department.name}</p>
                <p className="mt-0.5 text-xs text-faint">
                  Trưởng phòng: {leadName(department.lead)}
                </p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => openEdit(department)}
              >
                Sửa
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  setDeleteError(null);
                  setDeleteTarget(department);
                }}
              >
                Xoá
              </Button>
            </div>
          ))}
        </Card>
      )}

      <DepartmentFormModal
        open={formOpen}
        onClose={() => setFormOpen(false)}
        department={editDepartment}
        users={users ?? []}
      />
      <ConfirmDialog
        open={!!deleteTarget}
        title="Xoá phòng ban"
        message={`Xoá phòng ban "${deleteTarget?.name}"?`}
        loading={deleteDepartment.isPending}
        error={deleteError}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
