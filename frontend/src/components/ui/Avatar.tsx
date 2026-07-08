import { cn } from "@/lib/cn";

function initials(last?: string, first?: string): string {
  const a = (last ?? "").trim().charAt(0);
  const b = (first ?? "").trim().charAt(0);
  return (a + b).toUpperCase() || "?";
}

export function Avatar({
  src,
  lastName,
  firstName,
  className,
  textClassName,
}: {
  src?: string | null;
  lastName?: string;
  firstName?: string;
  // Box size + shape (e.g. "h-7 w-7").
  className?: string;
  // Initials type scale when no image is set (e.g. "text-[11px]").
  textClassName?: string;
}) {
  if (src) {
    return (
      // Backend returns dev /media or signed S3 URLs, not statically known paths.
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={src}
        alt=""
        className={cn("rounded-lg border border-line object-cover", className)}
      />
    );
  }
  return (
    <span
      className={cn(
        "grid place-items-center rounded-lg bg-line font-semibold text-ink-soft",
        textClassName,
        className,
      )}
    >
      {initials(lastName, firstName)}
    </span>
  );
}
