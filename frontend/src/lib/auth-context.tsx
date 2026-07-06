"use client";

import { createContext, useContext, useEffect, useState } from "react";

import {
  login as apiLogin,
  logout as apiLogout,
  restoreSession,
} from "@/lib/auth";

interface AuthState {
  ready: boolean;
  authed: boolean;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);

  // Access token lives in memory only; on load/reload, recover a session
  // silently from the refresh cookie before deciding the user is logged out.
  useEffect(() => {
    let active = true;
    restoreSession().then((ok) => {
      if (!active) return;
      setAuthed(ok);
      setReady(true);
    });
    return () => {
      active = false;
    };
  }, []);

  async function signIn(username: string, password: string) {
    await apiLogin(username, password);
    setAuthed(true);
  }

  async function signOut() {
    await apiLogout();
    setAuthed(false);
  }

  return (
    <AuthContext.Provider value={{ ready, authed, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
