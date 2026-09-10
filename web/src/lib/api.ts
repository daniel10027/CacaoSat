/**
 * Client HTTP typé pour l'API CacaoSat.
 * - injecte le Bearer token
 * - rafraîchit automatiquement sur 401 (une fois)
 * - normalise les erreurs -> ApiError
 */

export const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ??
  'http://localhost:8000/api/v1';

const ACCESS_KEY = 'cacaosat.access';
const REFRESH_KEY = 'cacaosat.refresh';

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  set(access: string, refresh?: string) {
    localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

export class ApiError extends Error {
  status: number;
  code: string;
  details: unknown;
  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

type Options = {
  method?: string;
  body?: unknown;
  auth?: boolean;
  signal?: AbortSignal;
  raw?: boolean;
};

let refreshing: Promise<boolean> | null = null;

async function doRefresh(): Promise<boolean> {
  const refresh = tokenStore.refresh;
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${refresh}` },
    });
    if (!res.ok) return false;
    const data = (await res.json()) as { access_token: string; refresh_token?: string };
    tokenStore.set(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

export async function api<T = unknown>(path: string, opts: Options = {}): Promise<T> {
  const { method = 'GET', body, auth = true, signal, raw = false } = opts;

  const send = async (): Promise<Response> => {
    const headers: Record<string, string> = {};
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    if (auth && tokenStore.access) headers.Authorization = `Bearer ${tokenStore.access}`;
    return fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  };

  let res = await send();

  if (res.status === 401 && auth && tokenStore.refresh) {
    refreshing = refreshing ?? doRefresh();
    const ok = await refreshing;
    refreshing = null;
    if (ok) {
      res = await send();
    } else {
      tokenStore.clear();
    }
  }

  if (raw) {
    if (!res.ok) throw new ApiError(res.status, 'http_error', res.statusText);
    return res as unknown as T;
  }

  const text = await res.text();
  const data = text ? (JSON.parse(text) as unknown) : null;

  if (!res.ok) {
    const err = (data as { error?: { code: string; message: string; details?: unknown } })?.error;
    throw new ApiError(
      res.status,
      err?.code ?? 'error',
      err?.message ?? `Erreur ${res.status}`,
      err?.details,
    );
  }
  return data as T;
}

export const downloadUrl = (path: string): string => `${API_URL}${path}`;
