"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { api, clearTokens, getAccess, getRefresh, setTokens } from "./api";
import type { Role, User } from "./types";

interface AuthState {
  user: User | null;
  status: "loading" | "ready";
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  reload: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export { homeFor } from "./routing";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<"loading" | "ready">("loading");

  const load = useCallback(async () => {
    if (!getAccess()) {
      setUser(null);
      setStatus("ready");
      return;
    }
    try {
      setUser(await api<User>("/auth/me/"));
    } catch {
      setUser(null);
    }
    setStatus("ready");
  }, []);

  useEffect(() => {
    const id = setTimeout(load, 0);
    return () => clearTimeout(id);
  }, [load]);

  useEffect(() => {
    const onExpired = () => setUser(null);
    window.addEventListener("sebms:session-expired", onExpired);
    return () => window.removeEventListener("sebms:session-expired", onExpired);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await api<{ access: string; refresh: string }>(
      "/auth/login/",
      { method: "POST", body: { email, password }, auth: false },
    );
    setTokens(data.access, data.refresh);
    const me = await api<User>("/auth/me/");
    setUser(me);
    return me;
  }, []);

  const logout = useCallback(async () => {
    const refresh = getRefresh();
    try {
      if (refresh) {
        await api("/auth/logout/", {
          method: "POST",
          body: { refresh },
          auth: false,
        });
      }
    } catch {
      // Token already invalid — clearing locally is enough.
    }
    clearTokens();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, status, login, logout, reload: load }),
    [user, status, login, logout, load],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export type { Role };
