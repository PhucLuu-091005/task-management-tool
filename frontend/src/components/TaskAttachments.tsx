"use client";

import { ImagePlus, Trash2, Upload } from "lucide-react";
import { ChangeEvent, FormEvent, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { fieldInput } from "@/components/ui/Field";
import { apiErrorMessage } from "@/lib/api";
import {
  ATTACHMENT_ACCEPT,
  attachmentError,
  useAttachments,
  useDeleteAttachment,
  useUploadAttachment,
} from "@/lib/attachments";

// Force a download of the attachment. Same-origin media (/media/* via the dev
// proxy) downloads directly; a cross-origin S3 URL that blocks the fetch falls
// back to opening in a new tab.
async function downloadAttachment(url: string, name: string) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(String(res.status));
    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(objectUrl);
  } catch {
    window.open(url, "_blank", "noopener,noreferrer");
  }
}

function attachmentFileName(url: string): string {
  return url.split("?")[0].split("/").pop() || "dinh-kem";
}

export default function TaskAttachments({
  taskId,
  canManage,
}: {
  taskId: number;
  canManage: (addedBy: number | null) => boolean;
}) {
  const { data: attachments, isPending } = useAttachments(taskId);
  const upload = useUploadAttachment(taskId);
  const remove = useDeleteAttachment(taskId);

  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [caption, setCaption] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handlePick(e: ChangeEvent<HTMLInputElement>) {
    const picked = e.target.files?.[0] ?? null;
    setError(picked ? attachmentError(picked) : null);
    setFile(picked);
  }

  function reset() {
    setFile(null);
    setCaption("");
    if (inputRef.current) inputRef.current.value = "";
  }

  function handleUpload(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    const invalid = attachmentError(file);
    if (invalid) {
      setError(invalid);
      return;
    }
    setError(null);
    upload.mutate(
      { file, caption: caption.trim() },
      {
        onSuccess: reset,
        onError: (err) =>
          setError(apiErrorMessage(err, "Không tải được ảnh lên.")),
      },
    );
  }

  return (
    <Card className="p-6">
      <h2 className="text-sm font-semibold tracking-tight">Đính kèm</h2>

      {isPending ? (
        <p className="mt-3 text-sm text-muted">Đang tải…</p>
      ) : attachments && attachments.length > 0 ? (
        <ul className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {attachments.map((att) => (
            <li key={att.id} className="group relative">
              <button
                type="button"
                onClick={() => {
                  void downloadAttachment(att.image, attachmentFileName(att.image));
                }}
                className="block w-full cursor-pointer"
                title="Tải ảnh về"
                aria-label={att.caption ? `Tải ảnh về: ${att.caption}` : "Tải ảnh về"}
              >
                {/* eslint-disable-next-line @next/next/no-img-element -- backend
                    returns signed S3 / dev media URLs, not statically known paths */}
                <img
                  src={att.image}
                  alt={att.caption || "Đính kèm"}
                  className="aspect-square w-full rounded-ctrl border border-line object-cover transition group-hover:opacity-95"
                />
              </button>
              {att.caption && (
                <p className="mt-1 truncate text-xs text-muted">{att.caption}</p>
              )}
              {canManage(att.added_by) && (
                <button
                  type="button"
                  onClick={() => {
                    setError(null);
                    remove.mutate(att.id, {
                      onError: (err) =>
                        setError(apiErrorMessage(err, "Không xoá được đính kèm.")),
                    });
                  }}
                  disabled={remove.isPending}
                  className="absolute right-1.5 top-1.5 grid h-7 w-7 place-items-center rounded-md bg-background/80 text-faint opacity-0 backdrop-blur-sm transition hover:text-status-over focus-visible:opacity-100 group-hover:opacity-100 disabled:opacity-50"
                  aria-label="Xoá đính kèm"
                >
                  <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                </button>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-muted">Chưa có đính kèm nào.</p>
      )}

      <form onSubmit={handleUpload} className="mt-4 border-t border-line pt-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-ctrl border border-line-strong bg-card px-3 py-2 text-sm text-ink transition hover:border-ink">
            <ImagePlus className="h-4 w-4 text-muted" strokeWidth={1.75} />
            {file ? "Đổi ảnh" : "Chọn ảnh"}
            <input
              ref={inputRef}
              type="file"
              accept={ATTACHMENT_ACCEPT}
              onChange={handlePick}
              className="sr-only"
            />
          </label>
          <input
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            aria-label="Chú thích"
            placeholder="Chú thích (tuỳ chọn)"
            className={`${fieldInput} flex-1`}
          />
          <Button
            type="submit"
            size="sm"
            disabled={!file || upload.isPending || !!attachmentError(file)}
          >
            <Upload className="h-4 w-4" strokeWidth={1.75} />
            Tải lên
          </Button>
        </div>
        {file && (
          <p className="mt-2 truncate text-xs text-muted">{file.name}</p>
        )}
        {error && <p className="mt-2 text-sm text-status-over">{error}</p>}
      </form>
    </Card>
  );
}
