export const DOCUMENTATION_FALLBACK_PATH = "/project-report.html";

export const DOCUMENTATION_HREF =
  process.env.NEXT_PUBLIC_DOCUMENTATION_URL?.trim() || DOCUMENTATION_FALLBACK_PATH;
