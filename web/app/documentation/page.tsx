const methodologySections = [
  {
    title: "1. Problem Definition",
    content:
      "The project addresses subjective answer sheet evaluation where traditional keyword matching is not enough. Students may write descriptive answers, draw diagrams, or solve mathematical expressions, so the system has to grade beyond plain text extraction.",
  },
  {
    title: "2. Input Design",
    content:
      "Each run starts with three required inputs: the ideal answer sheet, a rubric JSON file, and the student answer sheets. This keeps every evaluation traceable and allows the scoring logic to remain aligned with the academic marking scheme.",
  },
  {
    title: "3. Multimodal Processing",
    content:
      "After upload, the pipeline separates the sheet into multiple evidence streams. OCR captures the written answer, formula parsing handles mathematical expressions, and diagram extraction isolates visual regions so that each modality can be evaluated with a suitable method.",
  },
  {
    title: "4. Scoring Strategy",
    content:
      "The platform supports semantic scoring through SBERT and rubric-guided scoring through Gemini. The selected engine compares the student response with the ideal answer while using rubric weights to decide the final contribution of text, formulas, and diagrams.",
  },
  {
    title: "5. Result Delivery",
    content:
      "Once evaluation completes, the system stores structured JSON outputs, builds a ranked result table, and generates downloadable PDF reports for each student. This allows both technical analysis and faculty-level review from the same run.",
  },
];

const technologyRows = [
  ["Frontend", "Next.js", "Website interface for navigation, evaluation, documentation, and team pages"],
  ["Backend", "FastAPI", "API layer for uploads, runs, reports, and job history"],
  ["Printed OCR", "EasyOCR", "Text extraction from current and printed answer sheets"],
  ["Handwritten OCR", "Google Vision AI", "Recognition path for handwritten sheets"],
  ["Formula OCR", "pix2tex", "LaTeX conversion of mathematical expressions"],
  ["Math Validation", "SymPy", "Symbolic equivalence checking for formulas"],
  ["Diagram Handling", "OpenCV", "Region extraction and visual preprocessing"],
  ["Semantic Scoring", "Sentence Transformers (SBERT)", "Similarity scoring for descriptive answers"],
  ["LLM Scoring", "Gemini 2.5 Flash", "Rubric-aware grading using an LLM path"],
  ["Reporting", "FPDF2 + JSON", "Generation of PDF reports and structured result files"],
];

const outputRows = [
  ["Run metadata", "Stores configuration, timestamps, OCR mode, and evaluation engine."],
  ["Question-level JSON", "Keeps detailed scoring evidence for each answer."],
  ["Ranking table", "Shows total score, percentage, and ordering of students."],
  ["Student PDF report", "Provides a downloadable summary for each evaluated sheet."],
];

const diagramSteps = [
  "Ideal answer sheet + rubric + student sheets",
  "OCR and region extraction",
  "Text / formula / diagram processing",
  "SBERT or Gemini evaluation",
  "Ranking and report generation",
];

export default function DocumentationPage() {
  return (
    <article className="paper-page">
      <header className="paper-header">
        <p className="paper-header__type">Technical Documentation</p>
        <h1>Automated Subjective Answer Sheet Evaluation System</h1>
        <p className="paper-header__subtitle">
          A structured report-style page for the project architecture, workflow, tools,
          technologies, and current implementation design.
        </p>
        <div className="paper-meta">
          <span>B.Tech Project Workspace</span>
          <span>Multimodal Evaluation Pipeline</span>
          <span>Editable research-paper placeholder</span>
        </div>
      </header>

      <section className="paper-section">
        <h2>Abstract</h2>
        <p>
          The Automated Subjective Answer Sheet Evaluation System is designed to reduce manual
          effort in descriptive answer sheet checking by combining OCR, multimodal extraction,
          rubric-based scoring, and report generation into one connected platform. The system is
          intended for academic environments where answers may contain natural language, formulas,
          and diagrams, making simple keyword-based checking insufficient.
        </p>
      </section>

      <section className="paper-section">
        <h2>System Workflow</h2>
        <div className="paper-flow">
          {diagramSteps.map((step, index) => (
            <div key={step} className="paper-flow__item">
              <div className="paper-flow__node">
                <span>{index + 1}</span>
                <strong>{step}</strong>
              </div>
              {index < diagramSteps.length - 1 ? <div className="paper-flow__arrow" /> : null}
            </div>
          ))}
        </div>
      </section>

      <section className="paper-section">
        <h2>Methodology</h2>
        <div className="paper-section-grid">
          {methodologySections.map((section) => (
            <article key={section.title} className="paper-card">
              <h3>{section.title}</h3>
              <p>{section.content}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="paper-section">
        <h2>Tools and Technologies</h2>
        <div className="paper-table">
          <table>
            <thead>
              <tr>
                <th>Layer</th>
                <th>Tool / Technology</th>
                <th>Purpose</th>
              </tr>
            </thead>
            <tbody>
              {technologyRows.map(([layer, tech, purpose]) => (
                <tr key={`${layer}-${tech}`}>
                  <td>{layer}</td>
                  <td>{tech}</td>
                  <td>{purpose}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="paper-section">
        <h2>Output Artifacts</h2>
        <div className="paper-table">
          <table>
            <thead>
              <tr>
                <th>Artifact</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {outputRows.map(([artifact, description]) => (
                <tr key={artifact}>
                  <td>{artifact}</td>
                  <td>{description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="paper-section">
        <h2>Current Scope</h2>
        <p>
          The current website acts as a product-style interface over the research pipeline. It
          gives a cleaner entry point for evaluation, live workflow visibility, downloadable
          reports, and documentation. This page is intentionally structured like a paper so you can
          replace or extend the content later with your final research paper sections, figures, and
          citations.
        </p>
      </section>
    </article>
  );
}
