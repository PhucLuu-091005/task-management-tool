"use client";

import { FormEvent, useEffect, useState } from "react";

import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Field, fieldInput } from "@/components/ui/Field";
import { apiErrorMessage } from "@/lib/api";
import { useCreateTeam, useUpdateTeam } from "@/lib/admin";
import { Department, Team } from "@/lib/types";

export default function TeamFormModal({
  open,
  onClose,
  team,
  departments,
}: {
  open: boolean;
  onClose: () => void;
  team: Team | null;
  departments: Department[];
}) {
  const editing = !!team;
  const create = useCreateTeam();
  const update = useUpdateTeam(team?.id ?? 0);
  const mutation = editing ? update : create;

  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setName(team?.name ?? "");
    setDepartment(team?.department != null ? String(team.department) : "");
    setDescription(team?.description ?? "");
    setError(null);
  }, [open, team]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    mutation.mutate(
      {
        name: name.trim(),
        department: Number(department),
        description: description.trim(),
      },
      {
        onSuccess: onClose,
        onError: (err) =>
          setError(apiErrorMessage(err, "Không lưu được nhóm.")),
      },
    );
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={editing ? "Sửa nhóm" : "Tạo nhóm"}
    >
      {departments.length === 0 ? (
        <p className="text-sm text-muted">
          Cần tạo phòng ban trước khi tạo nhóm.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Tên nhóm" htmlFor="team-name">
            <input
              id="team-name"
              required
              maxLength={255}
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={fieldInput}
            />
          </Field>
          <Field label="Phòng ban" htmlFor="team-dept">
            <select
              id="team-dept"
              required
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className={fieldInput}
            >
              <option value="" disabled>
                Chọn phòng ban
              </option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Mô tả" htmlFor="team-desc">
            <textarea
              id="team-desc"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className={fieldInput}
            />
          </Field>
          {error && <p className="text-sm text-status-over">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={onClose}
            >
              Huỷ
            </Button>
            <Button type="submit" size="sm" disabled={mutation.isPending}>
              {editing ? "Lưu" : "Tạo"}
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
}
