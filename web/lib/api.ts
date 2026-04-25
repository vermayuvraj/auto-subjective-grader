const DEPRECATED_GPU_API_BASE_URL =
  "https://auto-subjective-grader-api-gpu-217944702445.asia-southeast1.run.app";
const DEFAULT_PRODUCTION_API_BASE_URL =
  "https://auto-subjective-grader-api-217944702445.asia-south1.run.app";

function normalizeBaseUrl(value?: string | null): string {
  return (value || "").trim().replace(/\/+$/, "");
}

function ensureApiSuffix(value?: string | null): string {
  const normalized = normalizeBaseUrl(value);
  if (!normalized) {
    return "";
  }
  return normalized.endsWith("/api") ? normalized : `${normalized}/api`;
}

function sanitizeServerBaseUrl(value?: string | null): string {
  const normalized = normalizeBaseUrl(value);
  return normalized === DEPRECATED_GPU_API_BASE_URL ? "" : normalized;
}

function getOrigin(value?: string | null): string {
  const normalized = normalizeBaseUrl(value);
  if (!normalized) {
    return "";
  }

  try {
    return new URL(normalized).origin;
  } catch {
    return normalized.replace(/\/api$/i, "");
  }
}

function isSameOrigin(candidate?: string | null, currentOrigin?: string | null): boolean {
  const current = normalizeBaseUrl(currentOrigin);
  if (!current) {
    return false;
  }

  return getOrigin(candidate) === current;
}

const SERVER_API_BASE_URL =
  process.env.NODE_ENV === "development"
    ? sanitizeServerBaseUrl(process.env.BACKEND_API_BASE_URL) ||
      sanitizeServerBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL) ||
      "http://127.0.0.1:8001"
    : sanitizeServerBaseUrl(process.env.BACKEND_API_BASE_URL) ||
      sanitizeServerBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL) ||
      DEFAULT_PRODUCTION_API_BASE_URL;

export function getBrowserApiBaseUrl(): string {
  if (process.env.NODE_ENV === "development") {
    return "/api";
  }

  const currentOrigin =
    typeof window !== "undefined" ? normalizeBaseUrl(window.location.origin) : "";
  const envBaseUrl = sanitizeServerBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL);
  const directBaseUrl =
    envBaseUrl && !isSameOrigin(envBaseUrl, currentOrigin)
      ? envBaseUrl
      : DEFAULT_PRODUCTION_API_BASE_URL;

  return ensureApiSuffix(directBaseUrl);
}

export const BROWSER_API_BASE_URL =
  process.env.NODE_ENV === "development"
    ? "/api"
    : ensureApiSuffix(DEFAULT_PRODUCTION_API_BASE_URL);

export function getServerApiBaseUrl(): string {
  const baseUrl = normalizeBaseUrl(SERVER_API_BASE_URL);
  if (!baseUrl) {
    throw new Error(
      "BACKEND_API_BASE_URL (or NEXT_PUBLIC_API_BASE_URL) is not configured for the server-side API proxy."
    );
  }
  return baseUrl;
}

export async function fetchJson<T>(path: string, fallback: T): Promise<T> {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  try {
    const response = await fetch(`${getServerApiBaseUrl()}${normalizedPath}`, {
      cache: "no-store",
    });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}
