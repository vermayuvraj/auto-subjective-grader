const CLOUD_RUN_API_BASE_URL =
  "https://auto-subjective-grader-api-gpu-217944702445.asia-southeast1.run.app";

function normalizeBaseUrl(value?: string | null): string {
  return (value || "").trim().replace(/\/+$/, "");
}

const SERVER_API_BASE_URL =
  process.env.NODE_ENV === "development"
    ? normalizeBaseUrl(process.env.BACKEND_API_BASE_URL) ||
      normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL) ||
      "http://127.0.0.1:8001"
    : normalizeBaseUrl(process.env.BACKEND_API_BASE_URL) ||
      normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL) ||
      CLOUD_RUN_API_BASE_URL;

const PUBLIC_API_BASE_URL =
  process.env.NODE_ENV === "development"
    ? normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL)
    : normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL) || CLOUD_RUN_API_BASE_URL;

export const BROWSER_API_BASE_URL = PUBLIC_API_BASE_URL
  ? `${PUBLIC_API_BASE_URL}/api`
  : "/api";

export function getServerApiBaseUrl(): string {
  return normalizeBaseUrl(SERVER_API_BASE_URL);
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
