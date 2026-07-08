"use client";

import { ImagePlus } from "lucide-react";
import { ChangeEvent, useState } from "react";

import Header from "@/components/Header";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Button, buttonStyles } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { apiErrorMessage } from "@/lib/api";
import { AVATAR_ACCEPT, avatarError } from "@/lib/avatar";
import {
  useProfile,
  useRemoveAvatar,
  useRequireAuth,
  useUpdateAvatar,
} from "@/lib/hooks";

export default function AccountPage() {
  const { data: user, isPending, isError, error } = useProfile();
  useRequireAuth(error);

  const updateAvatar = useUpdateAvatar();
  const removeAvatar = useRemoveAvatar();
  const [avatarErr, setAvatarErr] = useState<string | null>(null);

  function handlePick(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    // Reset so picking the same file again still fires onChange.
    e.target.value = "";
    if (!file) return;
    const invalid = avatarError(file);
    if (invalid) {
      setAvatarErr(invalid);
      return;
    }
    setAvatarErr(null);
    updateAvatar.mutate(file, {
      onError: (err) =>
        setAvatarErr(apiErrorMessage(err, "Không tải được ảnh lên.")),
    });
  }

  function handleRemove() {
    setAvatarErr(null);
    removeAvatar.mutate(undefined, {
      onError: (err) =>
        setAvatarErr(apiErrorMessage(err, "Không xoá được ảnh.")),
    });
  }

  if (isError) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-status-over">
          Không tải được thông tin tài khoản. Vui lòng thử lại.
        </p>
      </main>
    );
  }

  if (isPending || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted">Đang tải…</p>
      </main>
    );
  }

  const uploading = updateAvatar.isPending;
  // Upload and remove hit the same route; only one write may be in flight at a
  // time, or a late-resolving PATCH could desync the cache/DB and orphan a file.
  const busy = uploading || removeAvatar.isPending;

  return (
    <main className="min-h-screen">
      <Header />

      <div className="mx-auto max-w-5xl space-y-6 px-4 py-8">
        <h1 className="text-lg font-semibold tracking-tight">Tài khoản</h1>

        <Card className="p-6">
          <h2 className="text-[13px] font-medium uppercase tracking-wide text-faint">
            Thông tin
          </h2>

          <div className="mt-4 flex items-center gap-4">
            <Avatar
              src={user.avatar}
              lastName={user.last_name}
              firstName={user.first_name}
              className="h-20 w-20"
              textClassName="text-2xl"
            />
            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <label
                  className={buttonStyles(
                    "secondary",
                    "sm",
                    "cursor-pointer focus-within:ring-2 focus-within:ring-ink focus-within:ring-offset-2 focus-within:ring-offset-background",
                  )}
                  aria-disabled={busy}
                >
                  <ImagePlus className="h-4 w-4 text-muted" strokeWidth={1.75} />
                  {uploading ? "Đang tải…" : "Đổi ảnh"}
                  <input
                    type="file"
                    accept={AVATAR_ACCEPT}
                    onChange={handlePick}
                    disabled={busy}
                    className="sr-only"
                  />
                </label>
                {user.avatar && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleRemove}
                    disabled={busy}
                  >
                    Xoá ảnh
                  </Button>
                )}
              </div>
              <p className="text-xs text-faint">
                JPEG, PNG, GIF hoặc WEBP · tối đa 2MB.
              </p>
              {avatarErr && (
                <p className="text-sm text-status-over">{avatarErr}</p>
              )}
            </div>
          </div>

          <dl className="mt-6 grid gap-x-8 gap-y-3 border-t border-line pt-5 text-sm sm:grid-cols-2">
            <div className="flex justify-between sm:block">
              <dt className="text-muted">Họ tên</dt>
              <dd className="mt-0 font-medium sm:mt-1">
                {user.last_name} {user.first_name}
                {user.is_admin && <Badge className="ml-2">Admin</Badge>}
              </dd>
            </div>
            <div className="flex justify-between sm:block">
              <dt className="text-muted">Tên đăng nhập</dt>
              <dd className="mt-0 font-medium sm:mt-1">{user.username}</dd>
            </div>
            <div className="flex justify-between sm:block">
              <dt className="text-muted">Email</dt>
              <dd className="mt-0 font-medium sm:mt-1">{user.email}</dd>
            </div>
          </dl>
        </Card>

        <Card className="p-6">
          <h2 className="text-[13px] font-medium uppercase tracking-wide text-faint">
            Nhóm của tôi
          </h2>
          {user.memberships.length === 0 ? (
            <p className="mt-4 text-sm text-muted">Bạn chưa thuộc nhóm nào.</p>
          ) : (
            <ul className="mt-4 divide-y divide-line overflow-hidden rounded-ctrl border border-line">
              {user.memberships.map((m) => (
                <li
                  key={m.team}
                  className="flex items-center justify-between px-3.5 py-2.5 text-sm"
                >
                  <span className="font-medium">{m.team_name}</span>
                  <span className="text-xs text-muted">
                    {m.role === "leader" ? "Trưởng nhóm" : "Thành viên"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </main>
  );
}
