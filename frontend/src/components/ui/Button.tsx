import { forwardRef } from "react";

import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

const base =
  "inline-flex items-center justify-center gap-2 whitespace-nowrap font-medium rounded-ctrl transition-[background,border-color,color,transform] duration-150 active:translate-y-px active:scale-[.99] disabled:opacity-50 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-2 focus-visible:ring-offset-background";

const variants: Record<Variant, string> = {
  primary: "bg-ink text-white hover:bg-black shadow-soft-sm",
  secondary: "bg-card text-ink border border-line-strong hover:border-ink",
  ghost: "text-muted hover:text-ink hover:bg-line/60",
  danger:
    "bg-card text-status-over border border-status-over/25 hover:bg-status-over/5",
};

const sizes: Record<Size, string> = {
  sm: "text-[13px] px-3 py-1.5",
  md: "text-sm px-4 py-2.5",
};

export function buttonStyles(
  variant: Variant = "primary",
  size: Size = "md",
  className?: string,
): string {
  return cn(base, variants[variant], sizes[size], className);
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", size = "md", className, ...props },
  ref,
) {
  return (
    <button ref={ref} className={buttonStyles(variant, size, className)} {...props} />
  );
});
