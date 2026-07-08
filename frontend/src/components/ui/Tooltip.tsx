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
        // Right-anchored + w-max: an absolute child's auto width would shrink to
        // the (button-sized) wrapper and wrap one word per line, so size it to its
        // content and cap it, extending leftward from a right-aligned trigger.
        className="pointer-events-none absolute right-0 top-full z-50 mt-1.5 w-max max-w-[15rem] rounded-md bg-ink px-2.5 py-1.5 text-xs font-medium leading-snug text-white opacity-0 shadow-soft transition-opacity duration-100 group-hover/tt:opacity-100 group-focus-within/tt:opacity-100"
      >
        {label}
      </span>
    </span>
  );
}
