import type { ApiEnvelope } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

const ACCESS_KEY = "sebms_access";
const REFRESH_KEY = "sebms_refresh";
const EXPIRED_EVENT = "sebms:session-expired";

export class ApiError extends Error {
  code: string;
  status: number;
  details: unknown;

  constructor(
    message: string,
    code = "error",
    status = 0,
    details: unknown = null,
  ) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export function getAccess(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefresh(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

function emitSessionExpired(): void {
  clearTokens();
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(EXPIRED_EVENT));
  }
}

async function tryRefresh(): Promise<boolean> {
  const refresh = getRefresh();
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_URL}/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
      cache: "no-store",
    });
    if (!res.ok) return false;
    const env = (await res.json()) as ApiEnvelope<{ access: string; refresh?: string }>;
    if (!env.success || !env.data?.access) return false;
    setTokens(env.data.access, env.data.refresh ?? refresh);
    return true;
  } catch {
    return false;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  formData?: FormData;
  auth?: boolean;
}

async function request<T>(
  path: string,
  opts: RequestOptions = {},
  retried = false,
): Promise<T> {
  const auth = opts.auth !== false;
  const headers: Record<string, string> = {};
  const token = auth ? getAccess() : null;
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let payload: BodyInit | undefined;
  if (opts.formData) {
    payload = opts.formData;
  } else if (opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(opts.body);
  }

  const method =
    opts.method ?? (opts.body !== undefined || opts.formData ? "POST" : "GET");
  const url = path.startsWith("http") ? path : `${API_URL}${path}`;

  let res: Response;
  try {
    res = await fetch(url, {
      method,
      headers,
      body: payload,
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      "Cannot reach the API server. Is the backend running?",
      "network_error",
      0,
    );
  }

  if (res.status === 401 && auth && !retried && !path.startsWith("/auth/")) {
    if (await tryRefresh()) {
      return request<T>(path, opts, true);
    }
    emitSessionExpired();
    throw new ApiError(
      "Session expired. Please log in again.",
      "unauthenticated",
      401,
    );
  }

  let envelope: ApiEnvelope<T> | null = null;
  try {
    envelope = (await res.json()) as ApiEnvelope<T>;
  } catch {
    envelope = null;
  }

  if (!res.ok || !envelope || envelope.success !== true) {
    const err = envelope?.error;
    throw new ApiError(
      err?.message ?? `Request failed with status ${res.status}.`,
      err?.code ?? "http_error",
      res.status,
      err?.details ?? null,
    );
  }
  return envelope.data as T;
}

export function api<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  return request<T>(path, opts);
}
