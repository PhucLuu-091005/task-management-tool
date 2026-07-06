import { cn } from "@/lib/cn";

export function FeatureCell({
  className,
  invert,
  icon,
  title,
  body,
}: {
  className?: string;
  invert?: boolean;
  icon: React.ReactNode;
  title: string;
  body: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col rounded-card border p-6",
        invert ? "border-ink bg-ink text-white" : "border-line bg-card",
        className,
      )}
    >
      <span
        className={cn(
          "mb-4 grid h-10 w-10 place-items-center rounded-ctrl",
          invert
            ? "bg-white/10 text-white"
            : "border border-line bg-background text-ink",
        )}
      >
        {icon}
      </span>
      <h3 className="text-[17px] font-semibold tracking-tight">{title}</h3>
      <p
        className={cn(
          "mt-2 text-sm leading-relaxed",
          invert ? "text-white/70" : "text-muted",
        )}
      >
        {body}
      </p>
    </div>
  );
}

export function Step({
  n,
  title,
  body,
}: {
  n: string;
  title: string;
  body: string;
}) {
  return (
    <div className="border-t-2 border-ink pt-4">
      <div className="text-xs tabular-nums text-faint">{n}</div>
      <h3 className="mt-2 text-[17px] font-semibold tracking-tight">{title}</h3>
      <p className="mt-1.5 text-sm leading-snug text-muted">{body}</p>
    </div>
  );
}

const CHIP: Record<string, string> = {
  new: "bg-status-newbg text-status-new",
  prog: "bg-status-progbg text-status-prog",
  over: "bg-status-overbg text-status-over",
};

export function HeroPreview() {
  return (
    <div className="overflow-hidden rounded-card border border-line bg-card shadow-soft">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <div className="flex gap-1 text-[13px]">
          <span className="rounded-md bg-line px-2.5 py-1 font-medium text-ink">
            Tổng quan
          </span>
          <span className="px-2.5 py-1 text-muted">Công việc</span>
        </div>
        <span className="flex items-center gap-2 rounded-md border border-line px-2.5 py-1 text-xs text-faint">
          Tìm kiếm <span className="text-[10px]">⌘K</span>
        </span>
      </div>
      <div className="p-4">
        <div className="mb-4 grid grid-cols-4 divide-x divide-line overflow-hidden rounded-ctrl border border-line">
          <PreviewStat k="Tổng" v="48" />
          <PreviewStat k="Mới" v="12" dot="#4b5563" />
          <PreviewStat k="Đang xử lý" v="19" dot="#a65a0b" />
          <PreviewStat k="Quá hạn" v="3" dot="#c7362b" over />
        </div>
        <PreviewRow
          title="Chuẩn bị báo cáo quý"
          meta="cá nhân · hạn 05.07"
          chip="Quá hạn"
          tone="over"
        />
        <PreviewRow
          title="Rà soát hợp đồng nhà cung cấp"
          meta="nhóm pháp lý · hạn 12.07"
          chip="Đang xử lý"
          tone="prog"
        />
        <PreviewRow
          title="Cập nhật tài liệu onboarding"
          meta="phòng nhân sự · hạn 20.07"
          chip="Mới"
          tone="new"
          last
        />
      </div>
    </div>
  );
}

function PreviewStat({
  k,
  v,
  dot,
  over,
}: {
  k: string;
  v: string;
  dot?: string;
  over?: boolean;
}) {
  return (
    <div className="px-3 py-2.5">
      <p className="flex items-center gap-1.5 text-[11px] text-muted">
        {dot && (
          <span
            className="h-1.5 w-1.5 rounded-full"
            style={{ background: dot }}
          />
        )}
        {k}
      </p>
      <p
        className={cn(
          "mt-0.5 text-xl font-semibold tabular-nums tracking-tight",
          over && "text-status-over",
        )}
      >
        {v}
      </p>
    </div>
  );
}

function PreviewRow({
  title,
  meta,
  chip,
  tone,
  last,
}: {
  title: string;
  meta: string;
  chip: string;
  tone: keyof typeof CHIP;
  last?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 py-2.5",
        !last && "border-b border-line",
      )}
    >
      <div className="min-w-0 flex-1">
        <p className="text-[13px] font-medium">{title}</p>
        <p className="mt-0.5 text-[11px] text-faint">{meta}</p>
      </div>
      <span
        className={cn(
          "rounded-full px-2 py-0.5 text-[11px] font-medium",
          CHIP[tone],
        )}
      >
        {chip}
      </span>
    </div>
  );
}
