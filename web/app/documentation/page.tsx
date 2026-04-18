import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { DOCUMENTATION_HREF } from "../../lib/documentation";
import { SITE_NAME, absoluteUrl } from "../../lib/seo";

export const metadata: Metadata = {
  title: "Documentation",
  description:
    "Detailed project documentation for Ai Grader, including workflow design, libraries, models, OCR methods, evaluation pipeline, and implementation notes.",
  alternates: {
    canonical: absoluteUrl(DOCUMENTATION_HREF),
  },
  openGraph: {
    title: `Documentation | ${SITE_NAME}`,
    description:
      "Read the complete project report for Ai Grader, including architecture, models, OCR stack, evaluation logic, and implementation details.",
    url: absoluteUrl(DOCUMENTATION_HREF),
  },
};

export default function DocumentationPage() {
  redirect(DOCUMENTATION_HREF);
}
