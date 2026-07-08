import { cn } from "@/lib/cn";

const pill =
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium";

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
