import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "@/lib/auth-storage";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = axios.create({ baseURL: `${API_URL}/api` });

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error("Missing refresh token");
  // Plain axios: the api instance would attach the stale access token.
  const res = await axios.post(`${API_URL}/api/users/token/refresh`, {
    refresh,
  });
  // ROTATE_REFRESH_TOKENS is on server-side, so a new refresh token comes back too.
  setTokens({ access: res.data.access, refresh: res.data.refresh ?? refresh });
  return res.data.access;
}

type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean };

api.interceptors.response.use(undefined, async (error: AxiosError) => {
  const original = error.config as RetriableConfig | undefined;
  if (
    error.response?.status === 401 &&
    original &&
    !original._retried &&
    getRefreshToken()
  ) {
    original._retried = true;
    try {
      refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
      const access = await refreshPromise;
      original.headers.Authorization = `Bearer ${access}`;
      return api(original);
    } catch {
      clearTokens();
    }
  }
  return Promise.reject(error);
});

export function apiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error) && error.response?.data) {
    const data = error.response.data as Record<string, unknown>;
    if (typeof data.detail === "string") return data.detail;
    const first = Object.values(data)[0];
    if (Array.isArray(first) && typeof first[0] === "string") return first[0];
    if (typeof first === "string") return first;
  }
  return fallback;
}
