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

import { buttonStyles } from "@/components/ui/Button";
import { FeatureCell, HeroPreview, Step } from "@/components/landing";
import { useAuth } from "@/lib/auth-context";

export default function LandingPage() {
  const { authed } = useAuth();

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
                  Đăng ký
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
