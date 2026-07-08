import { cn } from "@/lib/cn";

// Hover/focus tooltip. The wrapper (not the child) is the hover target, so it
// still shows a reason over a *disabled* control — the intended use is pairing a
// disabled action with an explanation of why it's unavailable.
export function Tooltip({
  label,
  children,
  className,
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span className={cn("group/tt relative inline-flex", className)}>
      {children}
      <span
        role="tooltip"
        className="pointer-events-none absolute left-1/2 top-full z-50 mt-1.5 max-w-[16rem] -translate-x-1/2 rounded-md bg-ink px-2 py-1 text-center text-xs font-medium text-white opacity-0 shadow-soft transition-opacity duration-100 group-hover/tt:opacity-100 group-focus-within/tt:opacity-100"
      >
        {label}
      </span>
    </span>
  );
}
