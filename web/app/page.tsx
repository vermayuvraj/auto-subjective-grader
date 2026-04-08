import Link from "next/link";
import { SectionShell } from "../components/section-shell";

const signalCards = [
  {
    label: "OCR Modes",
    value: "2",
    detail: "Printed sheets with EasyOCR and handwritten sheets with Azure Document Intelligence.",
  },
  {
    label: "Evaluation Paths",
    value: "2",
    detail: "Fast local SBERT flow plus Gemini-assisted grading when needed.",
  },
  {
    label: "Knowledge Modes",
    value: "3",
    detail: "Text, formulas, and diagrams are processed as separate grading signals.",
  },
];

const modules = [
  {
    title: "Document Capture",
    text: "Uploads, rubric validation, PDF ingestion, and per-run workspace setup keep every batch traceable.",
  },
  {
    title: "Recognition Layer",
    text: "OCR, formula reading, and diagram region extraction convert answer sheets into structured evidence.",
  },
  {
    title: "Scoring Engine",
    text: "SBERT, CLIP, SymPy, and optional Gemini grading combine into rubric-aware marking.",
  },
  {
    title: "Faculty Outputs",
    text: "Live run tracking, ranking tables, downloadable PDF reports, and reusable JSON artifacts.",
  },
];

const workflow = [
  {
    title: "1. Upload Inputs",
    desc: "Select the ideal answer sheet, rubric JSON, and the student batch for the run.",
  },
  {
    title: "2. Extract Signals",
    desc: "OCR reads the sheet while formula and diagram modules isolate non-text answer content.",
  },
  {
    title: "3. Evaluate Answers",
    desc: "The selected engine compares each student response against the ideal answer under rubric rules.",
  },
  {
    title: "4. Generate Reports",
    desc: "The pipeline stores JSON outputs, ranks students, and produces downloadable PDF reports.",
  },
];

const valuePillars = [
  "Built for subjective, descriptive, and multimodal answer sheets",
  "Supports handwritten OCR without changing the evaluation pipeline",
  "Separates formula correctness from normal semantic text matching",
  "Shows live stage-by-stage workflow instead of a black-box batch run",
];

export default function HomePage() {
  return (
    <>
      <section className="hero-panel hero-panel--product">
        <div className="hero-layout hero-layout--product">
          <div className="hero-copy">
            <span className="hero-chip">BTP Product Workspace</span>
            <h1>Professional grading experience for multimodal answer-sheet evaluation.</h1>
            <p>
              This platform turns your research pipeline into a product-style interface for OCR,
              formula interpretation, diagram analysis, scoring, and faculty-ready reporting.
            </p>
            <div className="hero-actions">
              <Link href="/evaluate" className="button-primary">
                Launch Evaluation
              </Link>
              <Link href="/documentation" className="button-secondary">
                Explore Documentation
              </Link>
            </div>
            <div className="hero-pills">
              {valuePillars.map((pillar) => (
                <span key={pillar} className="hero-pill">
                  {pillar}
                </span>
              ))}
            </div>
          </div>

          <div className="hero-visual hero-visual--dashboard">
            <article className="spotlight-card spotlight-card--primary">
              <span className="spotlight-card__eyebrow">Product Snapshot</span>
              <strong>Unified pipeline from upload to scoring report</strong>
              <p>
                The same engine powers printed-sheet OCR, handwritten OCR, formula scoring,
                diagram comparison, and final report generation.
              </p>
              <div className="hero-score-strip">
                <div>
                  <span>Workflow</span>
                  <strong>Live tracked</strong>
                </div>
                <div>
                  <span>Reports</span>
                  <strong>PDF + JSON</strong>
                </div>
                <div>
                  <span>Interface</span>
                  <strong>Web + Streamlit</strong>
                </div>
              </div>
            </article>

            <div className="signal-grid">
              {signalCards.map((item) => (
                <article key={item.label} className="signal-card">
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                  <p>{item.detail}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>

      <SectionShell
        title="Core Product Modules"
        subtitle="The interface is now focused around the exact capabilities needed to demonstrate the project as a polished academic product."
      >
        <div className="module-grid">
          {modules.map((item, index) => (
            <article key={item.title} className={`module-card module-card--${index + 1}`}>
              <div className="module-card__number">0{index + 1}</div>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </SectionShell>

      <SectionShell
        title="Simple Connected Workflow"
        subtitle="Each stage feeds the next one so your guide can understand the system as a clean end-to-end product flow."
      >
        <div className="workflow-rail">
          {workflow.map((step, index) => (
            <div key={step.title} className="workflow-rail__item">
              <article className="workflow-node">
                <h3>{step.title}</h3>
                <p>{step.desc}</p>
              </article>
              {index < workflow.length - 1 ? <div className="workflow-rail__connector" /> : null}
            </div>
          ))}
        </div>
      </SectionShell>
    </>
  );
}
