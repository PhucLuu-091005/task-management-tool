// Mirror the backend limits (apps/users/validators.py) so the UI can reject a
// bad file before wasting an upload round-trip; the backend still enforces them.
export const AVATAR_MAX_BYTES = 2 * 1024 * 1024;
export const AVATAR_ACCEPT = "image/jpeg,image/png,image/gif,image/webp";
const ACCEPTED_TYPES = AVATAR_ACCEPT.split(",");

export function avatarError(file: File): string | null {
  if (!ACCEPTED_TYPES.includes(file.type)) {
    return "Chỉ chấp nhận ảnh JPEG, PNG, GIF hoặc WEBP.";
  }
  if (file.size > AVATAR_MAX_BYTES) {
    return "Ảnh vượt quá 2MB.";
  }
  return null;
}
