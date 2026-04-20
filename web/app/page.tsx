import type { Metadata } from "next";
import Link from "next/link";
import { SectionShell } from "../components/section-shell";
import { DOCUMENTATION_HREF } from "../lib/documentation";
import {
  SITE_DESCRIPTION,
  SITE_KEYWORDS,
  SITE_NAME,
  SITE_TITLE,
  absoluteUrl,
} from "../lib/seo";

export const metadata: Metadata = {
  title: SITE_TITLE,
  description: SITE_DESCRIPTION,
  keywords: SITE_KEYWORDS,
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: `${SITE_NAME} | ${SITE_TITLE}`,
    description: SITE_DESCRIPTION,
    url: absoluteUrl("/"),
  },
};

const quickSnapshot = [
  {
    title: "Input Pack",
    description:
      "The system accepts the ideal answer sheet, rubric JSON, and a batch of student PDFs for one traceable evaluation run.",
  },
  {
    title: "Recognition Layer",
    description:
      "Printed sheets use OCR extraction, while handwritten sheets can move through Google Vision AI for higher recognition quality.",
  },
  {
    title: "Multimodal Analysis",
    description:
      "Text, formula regions, and diagrams are treated as separate evidence streams instead of being flattened into plain OCR text only.",
  },
  {
    title: "Scoring and Reports",
    description:
      "The selected engine applies rubric-aware grading, generates ranking tables, and produces downloadable student reports.",
  },
];

const workflowSteps = [
  {
    step: "01",
    title: "Upload",
    description: "Faculty uploads the answer key, rubric JSON, and student answer sheets.",
  },
  {
    step: "02",
    title: "Extract",
    description: "OCR, formula parsing, and diagram isolation convert the sheets into structured answer signals.",
  },
  {
    step: "03",
    title: "Evaluate",
    description: "SBERT or Gemini compares answers against the ideal sheet while respecting rubric weights.",
  },
  {
    step: "04",
    title: "Deliver",
    description: "The platform returns run history, score tables, JSON outputs, and downloadable PDF reports.",
  },
];

const systemHighlights = [
  "Supports subjective answer sheet evaluation instead of only objective marking.",
  "Handles text answers, mathematical expressions, and diagrams in one pipeline.",
  "Supports both printed and handwritten answer sheet workflows.",
  "Provides an academic-friendly UI with traceable run history and report downloads.",
];

const useCases = [
  "College and university subjective exam paper evaluation",
  "Faculty workflows for rubric-based descriptive answer checking",
  "Handwritten and printed answer sheet digitization with OCR",
  "AI-assisted scoring for text, formulas, and diagram-heavy responses",
];

export default function HomePage() {
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "SoftwareApplication",
        name: SITE_NAME,
        applicationCategory: "EducationalApplication",
        operatingSystem: "Web",
        description: SITE_DESCRIPTION,
        url: absoluteUrl("/"),
        featureList: [
          "Subjective answer sheet evaluation",
          "Printed and handwritten OCR support",
          "Formula parsing and diagram-aware analysis",
          "Rubric-based scoring with report generation",
        ],
      },
      {
        "@type": "Organization",
        name: SITE_NAME,
        url: absoluteUrl("/"),
      },
      {
        "@type": "FAQPage",
        mainEntity: [
          {
            "@type": "Question",
            name: "What does Ai Grader do?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "Ai Grader helps evaluate subjective answer sheets by combining OCR, rubric-based scoring, semantic similarity, formula preparation, diagram analysis, and downloadable reporting.",
            },
          },
          {
            "@type": "Question",
            name: "Does Ai Grader support handwritten answer sheets?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "Yes. The platform supports handwritten answer sheet recognition through cloud OCR workflows alongside printed-sheet OCR for conventional scanned PDFs.",
            },
          },
        ],
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <section className="hero-panel home-overview">
        <div className="home-overview__layout">
          <div className="home-overview__copy">
            <span className="hero-chip">AI Answer Sheet Evaluation Platform</span>
            <h1>Automated Subjective Answer Sheet Evaluation System</h1>
            <p>
              Ai Grader is a web-based subjective answer sheet evaluation system designed for
              educators who want faster, more consistent grading of descriptive exam responses.
              It combines OCR, semantic grading, formula understanding, diagram-aware analysis,
              and rubric-based scoring in one connected workflow.
            </p>
            <p className="home-overview__secondary">
              The platform is built as a practical academic product where faculty can upload an
              ideal answer sheet, rubric JSON, and student PDFs, choose the evaluation mode,
              monitor the workflow, and download structured grading reports from a single
              interface.
            </p>
            <div className="hero-actions">
              <Link href="/evaluate" className="button-primary">
                Start Evaluation
              </Link>
              <Link
                href={DOCUMENTATION_HREF}
                className="button-secondary"
                target="_blank"
                rel="noreferrer"
              >
                Read Documentation
              </Link>
            </div>
          </div>

          <aside className="home-overview__panel">
            <span className="home-overview__eyebrow">Quick Snapshot</span>
            <strong>What the tool does in practice</strong>
            <div className="home-overview__list">
              {systemHighlights.map((item) => (
                <div key={item} className="home-overview__list-item">
                  <span className="home-overview__dot" />
                  <p>{item}</p>
                </div>
              ))}
            </div>
          </aside>
        </div>
      </section>

      <SectionShell
        title="Quick Snapshot"
        subtitle="A simplified view of how the system operates from file upload to final report generation."
      >
        <div className="snapshot-grid">
          {quickSnapshot.map((item) => (
            <article key={item.title} className="snapshot-card">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        title="How The Tool Works"
        subtitle="The full workflow is designed to stay simple for the user while the internal pipeline handles multimodal grading in sequence."
      >
        <div className="process-grid">
          {workflowSteps.map((item) => (
            <article key={item.step} className="process-card">
              <span className="process-card__step">{item.step}</span>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        title="Where It Can Be Used"
        subtitle="These search-aligned use cases describe the kinds of academic and evaluation problems the platform is built to solve."
      >
        <div className="snapshot-grid">
          {useCases.map((item) => (
            <article key={item} className="snapshot-card">
              <h3>{item}</h3>
              <p>
                The platform is suitable for this workflow because it combines OCR, rubric logic,
                and multimodal answer analysis instead of relying on plain keyword matching only.
              </p>
            </article>
          ))}
        </div>
      </SectionShell>
    </>
  );
}
