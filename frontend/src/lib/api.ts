import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/lib/auth-storage";

export const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let csrfReady: Promise<void> | null = null;

export function ensureCsrfToken(): Promise<void> {
  csrfReady ??= axios
    .get("/api/users/csrf/", { withCredentials: true })
    .then(() => undefined)
    .catch((err) => {
      csrfReady = null;
      throw err;
    });
  return csrfReady;
}

let refreshPromise: Promise<string> | null = null;

// Plain axios (not `api`): avoids attaching the stale access token and avoids
// re-entering this response interceptor on the refresh call itself.
async function doRefresh(): Promise<string> {
  await ensureCsrfToken();
  const res = await axios.post(
    "/api/users/token/refresh",
    {},
    {
      withCredentials: true,
      xsrfCookieName: "csrftoken",
      xsrfHeaderName: "X-CSRFToken",
    },
  );
  setAccessToken(res.data.access);
  return res.data.access;
}

// One shared in-flight refresh: the cold-start restore and the 401 interceptor
// must not rotate the refresh cookie twice concurrently (the 2nd would 401).
export function silentRefresh(): Promise<string> {
  refreshPromise ??= doRefresh().finally(() => {
    refreshPromise = null;
  });
  return refreshPromise;
}

type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean };

api.interceptors.response.use(undefined, async (error: AxiosError) => {
  const original = error.config as RetriableConfig | undefined;
  if (error.response?.status === 401 && original && !original._retried) {
    original._retried = true;
    try {
      const access = await silentRefresh();
      original.headers.Authorization = `Bearer ${access}`;
      return api(original);
    } catch {
      clearAccessToken();
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
