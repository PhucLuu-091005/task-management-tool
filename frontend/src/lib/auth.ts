import { api } from "@/lib/api";
import { clearTokens, getRefreshToken, setTokens } from "@/lib/auth-storage";
import { RegisterPayload, User } from "@/lib/types";

export async function login(username: string, password: string): Promise<void> {
  const res = await api.post("/users/login/", { username, password });
  setTokens(res.data);
}

export async function register(payload: RegisterPayload): Promise<User> {
  const res = await api.post("/users/register/", payload);
  return res.data;
}

export async function logout(): Promise<void> {
  const refresh = getRefreshToken();
  try {
    if (refresh) await api.post("/users/logout/", { refresh });
  } finally {
    clearTokens();
  }
}
