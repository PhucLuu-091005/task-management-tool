import { cn } from "@/lib/cn";
import { STATUS_BADGE_CLASSES, STATUS_LABELS } from "@/lib/labels";
import { TaskStatus } from "@/lib/types";

const pill =
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium";

export function StatusBadge({
  status,
  className,
}: {
  status: TaskStatus;
  className?: string;
}) {
  return (
    <span className={cn(pill, STATUS_BADGE_CLASSES[status], className)}>
      {STATUS_LABELS[status]}
    </span>
  );
}

export function Badge({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span className={cn(pill, "bg-line text-muted", className)}>{children}</span>
  );
}
