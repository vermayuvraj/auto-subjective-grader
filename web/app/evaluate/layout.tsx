import type { Metadata } from "next";
import { SITE_NAME, absoluteUrl } from "../../lib/seo";

export const metadata: Metadata = {
  title: "Evaluate Answer Sheets",
  description:
    "Upload an ideal answer sheet, rubric JSON, and student responses to run AI-powered subjective answer sheet evaluation with OCR, semantic scoring, and downloadable reports.",
  keywords: [
    "evaluate answer sheets",
    "subjective grading tool",
    "rubric json grading",
    "OCR answer sheet evaluation",
    "AI exam grading",
  ],
  alternates: {
    canonical: "/evaluate",
  },
  openGraph: {
    title: `Evaluate Answer Sheets | ${SITE_NAME}`,
    description:
      "Run the Ai Grader evaluation workflow with OCR extraction, formula parsing, semantic grading, and report generation.",
    url: absoluteUrl("/evaluate"),
  },
};

export default function EvaluateLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}

