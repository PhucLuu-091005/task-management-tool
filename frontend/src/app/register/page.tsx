"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { apiErrorMessage } from "@/lib/api";
import { hasSession } from "@/lib/auth-storage";
import { login, register } from "@/lib/auth";

const inputClass =
  "mt-1 w-full rounded-md border border-zinc-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-zinc-500 dark:border-zinc-700";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    username: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (hasSession()) router.replace("/");
  }, [router]);

  function setField(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(form);
      await login(form.username, form.password);
      router.replace("/");
    } catch (err) {
      setError(apiErrorMessage(err, "Đăng ký thất bại. Vui lòng thử lại sau."));
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-sm rounded-xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <h1 className="text-xl font-semibold">Đăng ký</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Tạo tài khoản để sử dụng hệ thống
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="last_name" className="block text-sm font-medium">
                Họ
              </label>
              <input
                id="last_name"
                value={form.last_name}
                onChange={setField("last_name")}
                required
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium">
                Tên
              </label>
              <input
                id="first_name"
                value={form.first_name}
                onChange={setField("first_name")}
                required
                className={inputClass}
              />
            </div>
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={form.email}
              onChange={setField("email")}
              required
              className={inputClass}
            />
          </div>
          <div>
            <label htmlFor="username" className="block text-sm font-medium">
              Tên đăng nhập
            </label>
            <input
              id="username"
              value={form.username}
              onChange={setField("username")}
              required
              className={inputClass}
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium">
              Mật khẩu
            </label>
            <input
              id="password"
              type="password"
              value={form.password}
              onChange={setField("password")}
              required
              minLength={8}
              className={inputClass}
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
          >
            {submitting ? "Đang đăng ký…" : "Đăng ký"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-zinc-500">
          Đã có tài khoản?{" "}
          <Link href="/login" className="font-medium underline">
            Đăng nhập
          </Link>
        </p>
      </div>
    </main>
  );
}
