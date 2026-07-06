"use client";

import { Activity } from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field, fieldInput } from "@/components/ui/Field";
import { apiErrorMessage } from "@/lib/api";
import { hasSession } from "@/lib/auth-storage";
import { login, register } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    username: "",
    password: "",
  });
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (hasSession()) router.replace("/tasks");
  }, [router]);

  function setField(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (form.password !== confirmPassword) {
      setError("Mật khẩu nhập lại không khớp.");
      return;
    }
    setSubmitting(true);
    try {
      await register(form);
      await login(form.username, form.password);
      router.replace("/tasks");
    } catch (err) {
      setError(apiErrorMessage(err, "Đăng ký thất bại. Vui lòng thử lại sau."));
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
          <span className="text-[15px] font-semibold tracking-tight">Chốt</span>
        </div>

        <h1 className="text-xl font-semibold tracking-tight">Đăng ký</h1>
        <p className="mt-1 text-sm text-muted">
          Tạo tài khoản để sử dụng hệ thống
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Field label="Họ" htmlFor="last_name">
              <input
                id="last_name"
                value={form.last_name}
                onChange={setField("last_name")}
                required
                className={fieldInput}
              />
            </Field>
            <Field label="Tên" htmlFor="first_name">
              <input
                id="first_name"
                value={form.first_name}
                onChange={setField("first_name")}
                required
                className={fieldInput}
              />
            </Field>
          </div>
          <Field label="Email" htmlFor="email">
            <input
              id="email"
              type="email"
              value={form.email}
              onChange={setField("email")}
              required
              className={fieldInput}
            />
          </Field>
          <Field label="Tên đăng nhập" htmlFor="username">
            <input
              id="username"
              value={form.username}
              onChange={setField("username")}
              required
              className={fieldInput}
            />
          </Field>
          <Field label="Mật khẩu" htmlFor="password">
            <input
              id="password"
              type="password"
              value={form.password}
              onChange={setField("password")}
              required
              minLength={8}
              className={fieldInput}
            />
          </Field>
          <Field label="Nhập lại mật khẩu" htmlFor="confirm_password">
            <input
              id="confirm_password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
              className={fieldInput}
            />
          </Field>

          {error && <p className="text-sm text-status-over">{error}</p>}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Đang đăng ký…" : "Đăng ký"}
          </Button>
        </form>

        <p className="mt-5 text-center text-sm text-muted">
          Đã có tài khoản?{" "}
          <Link
            href="/login"
            className="font-medium text-ink underline underline-offset-2"
          >
            Đăng nhập
          </Link>
        </p>
      </div>
    </main>
  );
}
