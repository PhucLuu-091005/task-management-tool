"use client";

import { ImagePlus, Link2, Plus, X } from "lucide-react";
import { ChangeEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { fieldInput } from "@/components/ui/Field";
import { ATTACHMENT_ACCEPT, attachmentError } from "@/lib/attachments";

export interface PendingLink {
  url: string;
  label: string;
}

export interface PendingImage {
  file: File;
}

// Collects links/images to attach right after a task is created (attachments
// are nested under an existing task, so the modal holds them until then).
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
  const [url, setUrl] = useState("");
  const [label, setLabel] = useState("");
  const [imgError, setImgError] = useState<string | null>(null);

  function addLink() {
    const trimmed = url.trim();
    if (!trimmed) return;
    onLinksChange([...links, { url: trimmed, label: label.trim() }]);
    setUrl("");
    setLabel("");
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
    onImagesChange([...images, ...files.map((file) => ({ file }))]);
  }

  return (
    <div className="space-y-4 border-t border-line pt-4">
      <div>
        <p className="mb-1.5 text-[13px] font-medium text-muted">
          Liên kết (tuỳ chọn)
        </p>
        {links.length > 0 && (
          <ul className="mb-2 space-y-1.5">
            {links.map((link, i) => (
              <li
                key={i}
                className="flex items-center gap-2 rounded-ctrl border border-line px-2.5 py-1.5 text-sm"
              >
                <Link2 className="h-4 w-4 shrink-0 text-faint" strokeWidth={1.75} />
                <span className="min-w-0 flex-1 truncate">
                  {link.label || link.url}
                </span>
                <button
                  type="button"
                  onClick={() => onLinksChange(links.filter((_, j) => j !== i))}
                  className="text-faint transition-colors hover:text-status-over"
                  aria-label="Xoá liên kết"
                >
                  <X className="h-4 w-4" strokeWidth={1.75} />
                </button>
              </li>
            ))}
          </ul>
        )}
        <div className="flex gap-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addLink();
              }
            }}
            placeholder="https://…"
            disabled={disabled}
            className={`${fieldInput} min-w-0 flex-1`}
          />
          <input
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="Nhãn"
            maxLength={200}
            disabled={disabled}
            className={`${fieldInput} w-24`}
          />
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={addLink}
            disabled={disabled || !url.trim()}
            aria-label="Thêm liên kết"
          >
            <Plus className="h-4 w-4" strokeWidth={2} />
          </Button>
        </div>
      </div>

      <div>
        <p className="mb-1.5 text-[13px] font-medium text-muted">Ảnh (tuỳ chọn)</p>
        {images.length > 0 && (
          <ul className="mb-2 flex flex-wrap gap-2">
            {images.map((img, i) => (
              <li
                key={i}
                className="flex items-center gap-1.5 rounded-ctrl border border-line px-2 py-1 text-xs"
              >
                <span className="max-w-[9rem] truncate">{img.file.name}</span>
                <button
                  type="button"
                  onClick={() => onImagesChange(images.filter((_, j) => j !== i))}
                  className="text-faint transition-colors hover:text-status-over"
                  aria-label="Bỏ ảnh"
                >
                  <X className="h-3.5 w-3.5" strokeWidth={1.75} />
                </button>
              </li>
            ))}
          </ul>
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
