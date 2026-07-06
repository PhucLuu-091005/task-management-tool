import { api, ensureCsrfToken, silentRefresh } from "@/lib/api";
import { clearAccessToken, setAccessToken } from "@/lib/auth-storage";
import { RegisterPayload, User } from "@/lib/types";

export async function login(username: string, password: string): Promise<void> {
  const res = await api.post("/users/login/", { username, password });
  setAccessToken(res.data.access);
}

export async function register(payload: RegisterPayload): Promise<User> {
  const res = await api.post("/users/register/", payload);
  return res.data;
}

export async function logout(): Promise<void> {
  try {
    await ensureCsrfToken();
    await api.post("/users/logout/", {});
  } finally {
    clearAccessToken();
  }
}

export async function restoreSession(): Promise<boolean> {
  try {
    await silentRefresh();
    return true;
  } catch {
    clearAccessToken();
    return false;
  }
}
