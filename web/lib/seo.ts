export const SITE_URL = "https://ai-grader.dev";
export const SITE_NAME = "Ai Grader";
export const SITE_TITLE = "Automated Subjective Answer Sheet Evaluation System";
export const SITE_DESCRIPTION =
  "Ai Grader is an AI-powered subjective answer sheet evaluation system for printed and handwritten exam papers, rubric-based grading, OCR extraction, formula parsing, diagram analysis, and downloadable reports.";
export const SITE_KEYWORDS = [
  "AI grader",
  "subjective answer sheet evaluation system",
  "automated subjective grading",
  "answer sheet evaluation tool",
  "AI answer sheet checker",
  "rubric based grading",
  "handwritten OCR grading",
  "printed answer sheet OCR",
  "exam paper evaluation system",
  "student answer sheet grading",
  "diagram and formula grading",
  "Gemini grading",
  "SBERT grading",
];
export const SITE_OG_IMAGE = "/brand/ai-grader-logo.png";

function normalizeGoogleVerificationToken(value: string | undefined): string {
  if (!value) {
    return "";
  }

  const trimmed = value.trim();
  const metaMatch = trimmed.match(/content\s*=\s*["']([^"']+)["']/i);
  if (metaMatch?.[1]) {
    return metaMatch[1].trim();
  }

  return trimmed.replace(/^["']+|["']+$/g, "").trim();
}

export const GOOGLE_SITE_VERIFICATION = normalizeGoogleVerificationToken(
  process.env.GOOGLE_SITE_VERIFICATION?.trim() ||
    process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION?.trim() ||
    "",
);

export function absoluteUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  return `${SITE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}
