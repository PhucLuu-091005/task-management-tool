"use client";

import { ImagePlus, Plus, X } from "lucide-react";
import { ChangeEvent, KeyboardEvent, useState } from "react";

import { fieldInput } from "@/components/ui/Field";
import { ATTACHMENT_ACCEPT, attachmentError } from "@/lib/attachments";

export interface PendingLink {
  url: string;
  label: string;
}

export interface PendingImage {
  file: File;
  caption: string;
}

// Collects links/images to attach right after a task is created (attachments
// are nested under an existing task, so the modal holds them until then). Every
// row is editable in place; the create step validates and skips empty rows.
export default function CreateTaskExtras({
  links,
  onLinksChange,
  images,
  onImagesChange,
  disabled,
}: {
  links: PendingLink[];
  onLinksChange: (links: PendingLink[]) => void;
  images: PendingImage[];
  onImagesChange: (images: PendingImage[]) => void;
  disabled?: boolean;
}) {
  const [imgError, setImgError] = useState<string | null>(null);

  function updateLink(i: number, patch: Partial<PendingLink>) {
    onLinksChange(links.map((l, j) => (j === i ? { ...l, ...patch } : l)));
  }
  function updateImage(i: number, caption: string) {
    onImagesChange(images.map((img, j) => (j === i ? { ...img, caption } : img)));
  }

  function pickImages(e: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    e.target.value = "";
    for (const file of files) {
      const invalid = attachmentError(file);
      if (invalid) {
        setImgError(invalid);
        return;
      }
    }
    setImgError(null);
    onImagesChange([...images, ...files.map((file) => ({ file, caption: "" }))]);
  }

  // Enter inside these sub-inputs would otherwise submit the whole task form.
  function stopEnter(e: KeyboardEvent) {
    if (e.key === "Enter") e.preventDefault();
  }

  const iconBtn =
    "grid h-9 w-9 shrink-0 place-items-center rounded-ctrl text-faint transition-colors hover:text-status-over disabled:opacity-50";

  return (
    <div className="space-y-4 border-t border-line pt-4">
      <div>
        <p className="mb-1.5 text-[13px] font-medium text-muted">
          Liên kết (tuỳ chọn)
        </p>
        {links.length > 0 && (
          <div className="space-y-2">
            {links.map((link, i) => (
              <div key={i} className="flex gap-2">
                <input
                  type="text"
                  value={link.url}
                  onChange={(e) => updateLink(i, { url: e.target.value })}
                  onKeyDown={stopEnter}
                  placeholder="https://…"
                  maxLength={500}
                  disabled={disabled}
                  className={`${fieldInput} min-w-0 flex-1`}
                />
                <input
                  value={link.label}
                  onChange={(e) => updateLink(i, { label: e.target.value })}
                  onKeyDown={stopEnter}
                  placeholder="Nhãn"
                  maxLength={200}
                  disabled={disabled}
                  className={`${fieldInput} shrink-0 basis-40`}
                />
                <button
                  type="button"
                  onClick={() => onLinksChange(links.filter((_, j) => j !== i))}
                  disabled={disabled}
                  className={iconBtn}
                  aria-label="Xoá liên kết"
                >
                  <X className="h-4 w-4" strokeWidth={1.75} />
                </button>
              </div>
            ))}
          </div>
        )}
        <button
          type="button"
          onClick={() => onLinksChange([...links, { url: "", label: "" }])}
          disabled={disabled}
          className="mt-2 inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink disabled:opacity-50"
        >
          <Plus className="h-4 w-4" strokeWidth={2} />
          Thêm liên kết
        </button>
      </div>

      <div>
        <p className="mb-1.5 text-[13px] font-medium text-muted">Ảnh (tuỳ chọn)</p>
        {images.length > 0 && (
          <div className="mb-2 space-y-2">
            {images.map((img, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="w-28 shrink-0 truncate text-xs text-muted">
                  {img.file.name}
                </span>
                <input
                  value={img.caption}
                  onChange={(e) => updateImage(i, e.target.value)}
                  onKeyDown={stopEnter}
                  placeholder="Tiêu đề ảnh (tuỳ chọn)"
                  maxLength={200}
                  disabled={disabled}
                  className={`${fieldInput} min-w-0 flex-1`}
                />
                <button
                  type="button"
                  onClick={() => onImagesChange(images.filter((_, j) => j !== i))}
                  disabled={disabled}
                  className={iconBtn}
                  aria-label="Bỏ ảnh"
                >
                  <X className="h-4 w-4" strokeWidth={1.75} />
                </button>
              </div>
            ))}
          </div>
        )}
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-ctrl border border-line-strong bg-card px-3 py-2 text-sm text-ink transition hover:border-ink">
          <ImagePlus className="h-4 w-4 text-muted" strokeWidth={1.75} />
          Chọn ảnh
          <input
            type="file"
            accept={ATTACHMENT_ACCEPT}
            multiple
            onChange={pickImages}
            disabled={disabled}
            className="sr-only"
          />
        </label>
        {imgError && <p className="mt-1.5 text-sm text-status-over">{imgError}</p>}
      </div>
    </div>
  );
}
