"use client";

import { FormEvent, useEffect, useState } from "react";

import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Field, fieldInput } from "@/components/ui/Field";
import { apiErrorMessage } from "@/lib/api";
import { useCreateDepartment, useUpdateDepartment } from "@/lib/admin";
import { userDisplayName } from "@/lib/labels";
import { Department, User } from "@/lib/types";

export default function DepartmentFormModal({
  open,
  onClose,
  department,
  users,
}: {
  open: boolean;
  onClose: () => void;
  department: Department | null;
  users: User[];
}) {
  const editing = !!department;
  const create = useCreateDepartment();
  const update = useUpdateDepartment(department?.id ?? 0);
  const mutation = editing ? update : create;

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [lead, setLead] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setName(department?.name ?? "");
    setDescription(department?.description ?? "");
    setLead(department?.lead != null ? String(department.lead) : "");
    setError(null);
  }, [open, department]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate(
      {
        name: name.trim(),
        description: description.trim(),
        lead: lead ? Number(lead) : null,
      },
      {
        onSuccess: onClose,
        onError: (err) =>
          setError(apiErrorMessage(err, "Không lưu được phòng ban.")),
      },
    );
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={editing ? "Sửa phòng ban" : "Tạo phòng ban"}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Tên phòng ban" htmlFor="dept-name">
          <input
            id="dept-name"
            required
            maxLength={255}
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={fieldInput}
          />
        </Field>
        <Field label="Mô tả" htmlFor="dept-desc">
          <textarea
            id="dept-desc"
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={fieldInput}
          />
        </Field>
        <Field label="Trưởng phòng" htmlFor="dept-lead">
          <select
            id="dept-lead"
            value={lead}
            onChange={(e) => setLead(e.target.value)}
            className={fieldInput}
          >
            <option value="">— Không —</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {userDisplayName(u)}
              </option>
            ))}
          </select>
        </Field>
        {error && <p className="text-sm text-status-over">{error}</p>}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" size="sm" onClick={onClose}>
            Huỷ
          </Button>
          <Button type="submit" size="sm" disabled={mutation.isPending}>
            {editing ? "Lưu" : "Tạo"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
