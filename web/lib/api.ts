const SERVER_API_BASE_URL =
  process.env.BACKEND_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8001";

const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "");

export const BROWSER_API_BASE_URL = PUBLIC_API_BASE_URL
  ? `${PUBLIC_API_BASE_URL}/api`
  : "/api";

export function getServerApiBaseUrl(): string {
  return SERVER_API_BASE_URL.replace(/\/+$/, "");
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
