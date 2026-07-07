"use client";

import { ExternalLink, Link2, Plus, Trash2 } from "lucide-react";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field, fieldInput } from "@/components/ui/Field";
import { apiErrorMessage } from "@/lib/api";
import { useAddLink, useDeleteLink, useLinks } from "@/lib/links";

export default function TaskLinks({
  taskId,
  canManage,
}: {
  taskId: number;
  canManage: (addedBy: number | null) => boolean;
}) {
  const { data: links, isPending } = useLinks(taskId);
  const addLink = useAddLink(taskId);
  const deleteLink = useDeleteLink(taskId);

  const [url, setUrl] = useState("");
  const [label, setLabel] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleAdd(e: FormEvent) {
    e.preventDefault();
    setError(null);
    addLink.mutate(
      { url: url.trim(), label: label.trim() },
      {
        onSuccess: () => {
          setUrl("");
          setLabel("");
        },
        onError: (err) =>
          setError(apiErrorMessage(err, "Không thêm được liên kết.")),
      },
    );
  }

  return (
    <Card className="p-6">
      <h2 className="text-sm font-semibold tracking-tight">Liên kết</h2>

      {isPending ? (
        <p className="mt-3 text-sm text-muted">Đang tải…</p>
      ) : links && links.length > 0 ? (
        <ul className="mt-3 divide-y divide-line">
          {links.map((link) => (
            <li key={link.id} className="flex items-center gap-3 py-2.5">
              <Link2
                className="h-4 w-4 shrink-0 text-faint"
                strokeWidth={1.75}
              />
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex min-w-0 items-center gap-1.5 text-sm text-ink hover:underline"
              >
                <span className="truncate">{link.label || link.url}</span>
                <ExternalLink className="h-3.5 w-3.5 shrink-0 text-faint" />
              </a>
              {canManage(link.added_by) && (
                <button
                  type="button"
                  onClick={() => {
                    setError(null);
                    deleteLink.mutate(link.id, {
                      onError: (err) =>
                        setError(apiErrorMessage(err, "Không xoá được liên kết.")),
                    });
                  }}
                  disabled={deleteLink.isPending}
                  className="ml-auto text-faint transition-colors hover:text-status-over disabled:opacity-50"
                  aria-label="Xoá liên kết"
                >
                  <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                </button>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-muted">Chưa có liên kết nào.</p>
      )}

      <form onSubmit={handleAdd} className="mt-4 border-t border-line pt-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <Field label="Đường dẫn" htmlFor="link-url" className="flex-1">
            <input
              id="link-url"
              type="url"
              required
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://…"
              className={fieldInput}
            />
          </Field>
          <Field label="Nhãn (tuỳ chọn)" htmlFor="link-label" className="flex-1">
            <input
              id="link-label"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              maxLength={200}
              placeholder="Tài liệu, thiết kế…"
              className={fieldInput}
            />
          </Field>
          <Button type="submit" size="sm" disabled={addLink.isPending}>
            <Plus className="h-4 w-4" strokeWidth={2} />
            Thêm
          </Button>
        </div>
        {error && <p className="mt-2 text-sm text-status-over">{error}</p>}
      </form>
    </Card>
  );
}
