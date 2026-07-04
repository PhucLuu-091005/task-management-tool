"use client";

import {
  Activity,
  ArrowRight,
  BarChart3,
  Clock,
  Paperclip,
  Search,
  Users,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { buttonStyles } from "@/components/ui/Button";
import { cn } from "@/lib/cn";
import { hasSession } from "@/lib/auth-storage";

export default function LandingPage() {
  const [authed, setAuthed] = useState(false);
  useEffect(() => setAuthed(hasSession()), []);

  const appHref = authed ? "/tasks" : "/login";
  const appLabel = authed ? "Vào ứng dụng" : "Đăng nhập";

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-line bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <span className="grid h-7 w-7 place-items-center rounded-lg bg-ink text-white">
              <Activity className="h-4 w-4" strokeWidth={2} />
            </span>
            <span className="text-[15px] font-semibold tracking-tight">Chốt</span>
          </Link>
          <nav className="hidden items-center gap-8 text-sm text-muted md:flex">
            <a href="#tinh-nang" className="transition-colors hover:text-ink">
              Tính năng
            </a>
            <a href="#cach-dung" className="transition-colors hover:text-ink">
              Cách dùng
            </a>
          </nav>
          <div className="flex items-center gap-2">
            {authed ? (
              <Link href="/tasks" className={buttonStyles("primary", "sm")}>
                Vào ứng dụng
              </Link>
            ) : (
              <>
                <Link href="/login" className={buttonStyles("ghost", "sm")}>
                  Đăng nhập
                </Link>
                <Link href="/register" className={buttonStyles("primary", "sm")}>
                  Dùng thử
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-6xl items-center gap-12 px-6 py-16 md:grid-cols-2 md:py-24">
        <div>
          <p className="text-sm text-muted">Quản lý công việc nội bộ</p>
          <h1 className="mt-4 text-4xl font-semibold leading-[1.05] tracking-tight md:text-5xl">
            Giao việc, chốt hạn,
            <br />
            theo đến khi xong.
          </h1>
          <p className="mt-5 max-w-md text-lg text-muted">
            Một nơi để giao việc cho cá nhân, nhóm hay phòng ban, theo dõi trạng
            thái và biết ngay việc nào sắp trễ hạn.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link href={appHref} className={buttonStyles("primary", "md")}>
              {appLabel}
              <ArrowRight className="h-4 w-4" strokeWidth={2} />
            </Link>
            <a href="#tinh-nang" className={buttonStyles("secondary", "md")}>
              Xem tính năng
            </a>
          </div>
        </div>
        <HeroPreview />
      </section>

      <section id="tinh-nang" className="border-t border-line">
        <div className="mx-auto max-w-6xl px-6 py-16 md:py-20">
          <h2 className="max-w-xl text-2xl font-semibold tracking-tight md:text-3xl">
            Đủ để điều phối cả phòng ban, không thừa một nút.
          </h2>
          <div className="mt-10 grid gap-4 md:grid-cols-6">
            <FeatureCell
              className="md:col-span-4"
              invert
              icon={<Users className="h-5 w-5" strokeWidth={1.75} />}
              title="Giao cho đúng đối tượng"
              body="Một công việc có thể thuộc về một cá nhân, một nhóm, hoặc cả phòng ban. Chọn kiểu giao việc khớp với cách tổ chức thật của bạn."
            />
            <FeatureCell
              className="md:col-span-2"
              icon={<Clock className="h-5 w-5" strokeWidth={1.75} />}
              title="Tự động quá hạn"
              body="Việc qua hạn hoàn thành tự chuyển trạng thái, không cần ai nhắc."
            />
            <FeatureCell
              className="md:col-span-2"
              icon={<BarChart3 className="h-5 w-5" strokeWidth={1.75} />}
              title="Tổng quan trực quan"
              body="Số liệu theo trạng thái, người phụ trách, nhóm và phòng ban."
            />
            <FeatureCell
              className="md:col-span-2"
              icon={<Search className="h-5 w-5" strokeWidth={1.75} />}
              title="Tìm và lọc nhanh"
              body="Tìm theo tiêu đề, lọc theo trạng thái và độ ưu tiên."
            />
            <FeatureCell
              className="md:col-span-2"
              icon={<Paperclip className="h-5 w-5" strokeWidth={1.75} />}
              title="Đính kèm và liên kết"
              body="Gắn hình ảnh và đường dẫn tài liệu ngay trong công việc."
            />
          </div>
        </div>
      </section>

      <section id="cach-dung" className="border-t border-line">
        <div className="mx-auto max-w-6xl px-6 py-16 md:py-20">
          <h2 className="max-w-xl text-2xl font-semibold tracking-tight md:text-3xl">
            Từ lúc tạo đến lúc xong, bốn bước.
          </h2>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <Step n="01" title="Tạo công việc" body="Đặt tiêu đề, mô tả, độ ưu tiên và hạn hoàn thành." />
            <Step n="02" title="Giao cho người phụ trách" body="Cá nhân, nhóm hoặc phòng ban, tùy việc." />
            <Step n="03" title="Theo dõi trạng thái" body="Cập nhật tiến độ và nhận cảnh báo khi sắp trễ." />
            <Step n="04" title="Hoàn thành" body="Đánh dấu xong và nhìn lại trên bảng tổng quan." />
          </div>
        </div>
      </section>

      <section className="border-t border-line">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <div className="flex flex-wrap items-center justify-between gap-6 rounded-[20px] bg-ink px-8 py-12 md:px-12">
            <div>
              <h2 className="max-w-md text-2xl font-semibold tracking-tight text-white md:text-3xl">
                Bắt đầu điều phối công việc gọn hơn.
              </h2>
              <p className="mt-3 text-[15px] text-white/60">
                Đăng nhập bằng tài khoản nội bộ và tạo công việc đầu tiên trong
                một phút.
              </p>
            </div>
            <Link
              href={appHref}
              className="inline-flex items-center gap-2 rounded-ctrl bg-white px-5 py-3 text-sm font-medium text-ink transition hover:bg-white/90 active:scale-[.99]"
            >
              {appLabel}
              <ArrowRight className="h-4 w-4" strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-10 text-sm text-muted">
          <div className="flex items-center gap-2">
            <span className="grid h-6 w-6 place-items-center rounded-md bg-ink text-white">
              <Activity className="h-3.5 w-3.5" strokeWidth={2} />
            </span>
            <span className="font-semibold text-ink">Chốt</span>
          </div>
          <span className="text-faint">Giao việc, chốt hạn, xong.</span>
        </div>
      </footer>
    </div>
  );
}

function FeatureCell({
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

function Step({ n, title, body }: { n: string; title: string; body: string }) {
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

function HeroPreview() {
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
