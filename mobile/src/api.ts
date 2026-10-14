import { API_URL } from "./config";
import * as storage from "./storage";

function extractMessage(data: any): string {
  if (!data) return "Something went wrong. Please try again.";
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) return data.detail.join(" ");
  const first = Object.values(data)[0];
  if (Array.isArray(first)) return String(first[0]);
  if (typeof first === "string") return first;
  return "Something went wrong. Please try again.";
}

export class ApiError extends Error {
  status: number;
  data: any;
  constructor(status: number, data: any) {
    super(extractMessage(data));
    this.status = status;
    this.data = data;
  }
}

let onAuthFailure: (() => void) | null = null;
export function setAuthFailureHandler(fn: (() => void) | null) {
  onAuthFailure = fn;
}

async function rawFetch(path: string, options: RequestInit, token?: string | null) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Device-Id": await storage.getDeviceId(),
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  return fetch(`${API_URL}${path}`, { ...options, headers });
}

// Returns a new access token, or null if the refresh token is no longer valid.
// A network failure throws, so a bad connection never logs the user out.
async function refreshAccess(): Promise<string | null> {
  const refresh = await storage.getRefresh();
  if (!refresh) return null;
  const res = await rawFetch("/auth/refresh/", {
    method: "POST",
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) return null;
  const data = await res.json();
  await storage.saveTokens(data.access, data.refresh);
  return data.access;
}

export async function request<T = any>(
  path: string,
  options: RequestInit = {},
  auth = true
): Promise<T> {
  let res = await rawFetch(path, options, auth ? await storage.getAccess() : null);

  if (auth && res.status === 401) {
    const fresh = await refreshAccess();
    if (!fresh) {
      onAuthFailure?.();
      throw new ApiError(401, { detail: "Session expired. Please log in again." });
    }
    res = await rawFetch(path, options, fresh);
  }

  const text = await res.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (!res.ok) throw new ApiError(res.status, data);
  return data as T;
}

export const login = (username: string, password: string) =>
  request<{ access: string; refresh: string; role: string }>(
    "/auth/login/",
    { method: "POST", body: JSON.stringify({ username, password }) },
    false
  );

export const me = () => request("/auth/me/");