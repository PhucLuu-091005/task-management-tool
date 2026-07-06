export const fieldInput =
  "w-full rounded-ctrl border border-line-strong bg-card px-3 py-2 text-sm text-ink outline-none transition placeholder:text-faint focus:border-ink focus:ring-4 focus:ring-line";

export const fieldLabel = "block text-[13px] font-medium text-muted mb-1.5";

export function Field({
  label,
  htmlFor,
  className,
  children,
}: {
  label: string;
  htmlFor?: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={className}>
      <label htmlFor={htmlFor} className={fieldLabel}>
        {label}
      </label>
      {children}
    </div>
  );
}
