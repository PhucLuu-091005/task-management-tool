import { ChevronLeft, ChevronRight } from "lucide-react";

import { cn } from "@/lib/cn";

// Google-style page list: always first + last, the current page and its
// neighbours, and "…" for the gaps.
function pageList(current: number, total: number): (number | "gap")[] {
  const shown = new Set<number>([
    1,
    total,
    current - 1,
    current,
    current + 1,
  ]);
  const sorted = Array.from(shown)
    .filter((p) => p >= 1 && p <= total)
    .sort((a, b) => a - b);

  const out: (number | "gap")[] = [];
  let prev = 0;
  for (const p of sorted) {
    if (p - prev > 1) out.push("gap");
    out.push(p);
    prev = p;
  }
  return out;
}

const cell =
  "grid h-8 min-w-8 place-items-center rounded-ctrl border px-2 text-sm tnum transition";
const inactive =
  "border-line-strong bg-card text-ink hover:border-ink disabled:opacity-40 disabled:hover:border-line-strong";

export function Pagination({
  page,
  total,
  onChange,
}: {
  page: number;
  total: number;
  onChange: (page: number) => void;
}) {
  if (total <= 1) return null;

  return (
    <nav className="flex items-center justify-center gap-1" aria-label="Phân trang">
      <button
        type="button"
        className={cn(cell, inactive)}
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
        aria-label="Trang trước"
      >
        <ChevronLeft className="h-4 w-4" strokeWidth={1.75} />
      </button>

      {pageList(page, total).map((item, i) =>
        item === "gap" ? (
          <span
            key={`gap-${i}`}
            className="grid h-8 w-8 place-items-center text-sm text-faint"
          >
            …
          </span>
        ) : (
          <button
            key={item}
            type="button"
            onClick={() => onChange(item)}
            aria-current={item === page ? "page" : undefined}
            className={cn(
              cell,
              item === page
                ? "border-ink bg-ink font-medium text-white"
                : inactive,
            )}
          >
            {item}
          </button>
        ),
      )}

      <button
        type="button"
        className={cn(cell, inactive)}
        disabled={page >= total}
        onClick={() => onChange(page + 1)}
        aria-label="Trang sau"
      >
        <ChevronRight className="h-4 w-4" strokeWidth={1.75} />
      </button>
    </nav>
  );
}
