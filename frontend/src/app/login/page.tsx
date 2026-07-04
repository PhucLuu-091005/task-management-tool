"use client";

import { Activity } from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field, fieldInput } from "@/components/ui/Field";
import { apiErrorMessage } from "@/lib/api";
import { hasSession } from "@/lib/auth-storage";
import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (hasSession()) router.replace("/");
  }, [router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      router.replace("/");
    } catch (err) {
      setError(
        apiErrorMessage(err, "Đăng nhập thất bại. Vui lòng thử lại sau."),
      );
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-sm rounded-card border border-line bg-card p-8 shadow-soft">
        <div className="mb-6 flex items-center gap-2.5">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-ink text-white">
            <Activity className="h-5 w-5" strokeWidth={2} />
          </span>
          <span className="text-[15px] font-semibold tracking-tight">
            Quản lý công việc
          </span>
        </div>

        <h1 className="text-xl font-semibold tracking-tight">Đăng nhập</h1>
        <p className="mt-1 text-sm text-muted">
          Hệ thống quản lý công việc nội bộ
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <Field label="Tên đăng nhập" htmlFor="username">
            <input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              className={fieldInput}
            />
          </Field>
          <Field label="Mật khẩu" htmlFor="password">
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className={fieldInput}
            />
          </Field>

          {error && <p className="text-sm text-status-over">{error}</p>}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Đang đăng nhập…" : "Đăng nhập"}
          </Button>
        </form>

        <p className="mt-5 text-center text-sm text-muted">
          Chưa có tài khoản?{" "}
          <Link
            href="/register"
            className="font-medium text-ink underline underline-offset-2"
          >
            Đăng ký
          </Link>
        </p>
      </div>
    </main>
  );
}
