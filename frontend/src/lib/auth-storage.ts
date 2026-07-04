const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

export interface TokenPair {
  access: string;
  refresh: string;
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens({ access, refresh }: TokenPair): void {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function hasSession(): boolean {
  return getAccessToken() !== null || getRefreshToken() !== null;
}
