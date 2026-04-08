import ReactMarkdown from "react-markdown";
import { SectionShell } from "../../components/section-shell";
import { fetchJson } from "../../lib/api";

type DocumentationResponse = {
  content: string;
};

const metrics = [
  { label: "OCR Backends", value: "2", detail: "EasyOCR and Azure Document Intelligence" },
  { label: "Scoring Engines", value: "2", detail: "SBERT local path and Gemini LLM path" },
  { label: "Modalities", value: "3", detail: "Text, diagrams, and formula understanding" },
  { label: "Primary Outputs", value: "3", detail: "JSON, live ranking table, and PDF reports" },
];

const architecture = [
  {
    title: "Frontend Layer",
    detail: "Next.js website plus Streamlit workspace for research-style testing.",
  },
  {
    title: "Backend Layer",
    detail: "FastAPI APIs, run management, job history, and report download endpoints.",
  },
  {
    title: "Core Evaluation Engine",
    detail: "Reusable Python pipeline powering OCR, formulas, diagrams, scoring, and reports.",
  },
];

const stageDetails = [
  {
    title: "Input and Run Setup",
    goal: "Collect the ideal answer sheet, rubric, and student answer sheets for a traceable batch run.",
    tech: "Next.js forms, FastAPI upload handling, JSON validation",
    points: [
      "The ideal answer sheet becomes the reference answer source.",
      "Rubric JSON controls marks distribution and weighting logic.",
      "Student PDFs are stored under per-run folders for reproducibility.",
    ],
  },
  {
    title: "OCR and Content Capture",
    goal: "Convert PDF pages into structured textual evidence.",
    tech: "pdf2image, Poppler, EasyOCR, Azure Document Intelligence",
    points: [
      "EasyOCR is used for cleaner printed answer sheets.",
      "Azure Document Intelligence is used for handwritten sheets.",
      "OCR output is stored page-wise for downstream reuse.",
    ],
  },
  {
    title: "Formula and Diagram Processing",
    goal: "Handle non-text answer content separately from regular prose.",
    tech: "pix2tex, SymPy, OpenCV, connected-component extraction",
    points: [
      "Formula-like regions are converted into LaTeX using pix2tex.",
      "SymPy checks mathematical equivalence rather than plain string similarity.",
      "Diagram regions are extracted independently for visual comparison.",
    ],
  },
  {
    title: "Scoring and Evaluation",
    goal: "Combine all answer signals under the rubric.",
    tech: "Sentence Transformers, CLIP, SymPy, Gemini 2.5 Flash",
    points: [
      "SBERT measures semantic answer similarity in the local evaluation path.",
      "CLIP compares extracted diagrams visually.",
      "Gemini acts as the LLM-based rubric-aware grading alternative.",
    ],
  },
  {
    title: "Reports and Delivery",
    goal: "Produce interpretable outputs for faculty and testing.",
    tech: "FPDF2, JSON serialization, tabular summaries, API report downloads",
    points: [
      "Each run produces structured JSON result artifacts.",
      "Each student receives a PDF evaluation report.",
      "The interfaces provide ranking tables and downloadable reports.",
    ],
  },
];

const outputArtifacts = [
  { artifact: "OCR JSON", purpose: "Page-wise extracted text, boxes, and OCR metadata." },
  { artifact: "Formula Results", purpose: "Detected expressions and LaTeX/SymPy comparison data." },
  { artifact: "Diagram Crops", purpose: "Visual regions used for diagram-level comparison." },
  { artifact: "Evaluation JSON", purpose: "Question-wise scoring, totals, and remarks." },
  { artifact: "PDF Reports", purpose: "Faculty-ready downloadable result summaries." },
];

const maturityBars = [
  { label: "Upload and validation", value: 100 },
  { label: "OCR processing", value: 100 },
  { label: "Formula understanding", value: 95 },
  { label: "Diagram extraction", value: 90 },
  { label: "Scoring workflow", value: 100 },
  { label: "Reporting", value: 100 },
];

const techPills = [
  "Next.js",
  "FastAPI",
  "Streamlit",
  "EasyOCR",
  "Azure Document Intelligence",
  "Sentence Transformers",
  "CLIP",
  "pix2tex",
  "SymPy",
  "Gemini 2.5 Flash",
  "FPDF2",
  "OpenCV",
];

const fallbackDocumentation = `# Documentation

The backend documentation endpoint is not reachable right now.

The sections above still summarize the current architecture, workflow, and technologies used in the project.`;

export default async function DocumentationPage() {
  const documentation = await fetchJson<DocumentationResponse>("/api/documentation", {
    content: fallbackDocumentation,
  });

  return (
    <>
      <SectionShell
        title="Documentation"
        subtitle="A product-style technical brief that explains the complete grading architecture, major stages, technologies, and output artifacts."
      >
        <div className="doc-metric-grid">
          {metrics.map((item) => (
            <article key={item.label} className="doc-metric-card">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <small>{item.detail}</small>
            </article>
          ))}
        </div>

        <div className="architecture-grid">
          {architecture.map((item) => (
            <article key={item.title} className="architecture-card">
              <h3>{item.title}</h3>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        title="Pipeline Readiness"
        subtitle="A quick visual indicator of how mature each major system block is in the current implementation."
      >
        <div className="doc-bars">
          {maturityBars.map((item) => (
            <div className="doc-bar-row" key={item.label}>
              <span>{item.label}</span>
              <div className="doc-bar-track">
                <div className="doc-bar-fill" style={{ width: `${item.value}%` }} />
              </div>
              <strong>{item.value}%</strong>
            </div>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        title="Stage-by-Stage Workflow"
        subtitle="This is the technical narrative you can use while explaining the project to your guide."
      >
        <div className="doc-stage-grid">
          {stageDetails.map((stage) => (
            <article key={stage.title} className="doc-stage-card">
              <div className="doc-stage-card__eyebrow">Tech used: {stage.tech}</div>
              <h3>{stage.title}</h3>
              <p>{stage.goal}</p>
              <ul>
                {stage.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        title="Tech Stack and Artifacts"
        subtitle="A concise view of what the product uses internally and what it produces after every run."
      >
        <div className="tech-pill-grid">
          {techPills.map((item) => (
            <span key={item} className="tech-pill">
              {item}
            </span>
          ))}
        </div>

        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Artifact</th>
                <th>Purpose</th>
              </tr>
            </thead>
            <tbody>
              {outputArtifacts.map((item) => (
                <tr key={item.artifact}>
                  <td>{item.artifact}</td>
                  <td>{item.purpose}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionShell>

      <SectionShell
        title="README Reference"
        subtitle="The current repository documentation is still rendered below for full technical traceability."
      >
        <article className="doc-shell">
          <ReactMarkdown>{documentation.content}</ReactMarkdown>
        </article>
      </SectionShell>
    </>
  );
}
