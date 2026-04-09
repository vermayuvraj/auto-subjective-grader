"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { SectionShell } from "../../components/section-shell";
import { BROWSER_API_BASE_URL } from "../../lib/api";

type SummaryRow = {
  rank: number;
  student: string;
  total_score: number;
  max_score: number;
  percentage: number;
};

type RunEvent = {
  timestamp: string;
  message: string;
};

type ReportLink = {
  student: string;
  download_url: string;
};

type RunMeta = {
  run_id: string;
  status: "queued" | "running" | "completed" | "failed";
  engine: string;
  ocr_backend: string;
  student_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  current_step: number;
  total_steps: number;
  progress_percent: number;
  message: string;
  events: RunEvent[];
  elapsed_seconds: number | null;
  eval_dir: string | null;
  report_dir: string | null;
  summary_rows: SummaryRow[];
  reports: ReportLink[];
  error: string | null;
};

type RunSummary = {
  run_id: string;
  status: RunMeta["status"];
  engine: string;
  ocr_backend: string;
  student_count: number;
  created_at: string;
  completed_at: string | null;
  elapsed_seconds: number | null;
  progress_percent: number;
  message: string;
  top_student: string | null;
  top_percentage: number | null;
};

type RuntimeConfig = {
  azure_configured: boolean;
  gemini_configured: boolean;
  allowed_origins: string[];
};

type WorkflowBlock = {
  key: string;
  title: string;
  detail: string;
  optional?: boolean;
};

const WORKFLOW_BLOCKS: WorkflowBlock[] = [
  {
    key: "input",
    title: "Input Ready",
    detail: "Uploads, rubric validation, and job creation",
  },
  {
    key: "ocr",
    title: "OCR Extraction",
    detail: "EasyOCR or Azure Document Intelligence",
  },
  {
    key: "formula",
    title: "Formula Parsing",
    detail: "pix2tex + SymPy preparation",
    optional: true,
  },
  {
    key: "diagram",
    title: "Diagram Extraction",
    detail: "OpenCV-based visual region detection",
  },
  {
    key: "evaluation",
    title: "Evaluation",
    detail: "SBERT / Gemini scoring with rubric logic",
  },
  {
    key: "report",
    title: "Report Generation",
    detail: "JSON outputs, ranking table, and PDF reports",
  },
];

function formatTimestamp(value: string | null): string {
  if (!value) {
    return "Not available";
  }

  try {
    return new Intl.DateTimeFormat("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatDuration(seconds: number | null): string {
  if (seconds === null || Number.isNaN(seconds)) {
    return "Pending";
  }

  if (seconds < 60) {
    return `${Math.round(seconds)} sec`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
}

function getEngineLabel(engine: string): string {
  return engine === "LLM" ? "Gemini 2.5 Flash" : "SBERT (fast, local)";
}

function getOcrLabel(ocrBackend: string): string {
  return ocrBackend === "azure"
    ? "Handwritten sheets (Azure Document Intelligence)"
    : "Current / printed sheets (EasyOCR)";
}

function getAveragePercentage(rows: SummaryRow[]): string {
  if (!rows.length) {
    return "--";
  }

  const average = rows.reduce((sum, row) => sum + row.percentage, 0) / rows.length;
  return `${average.toFixed(2)}%`;
}

function getStatusTone(status: RunMeta["status"] | RunSummary["status"]): string {
  return `status-badge is-${status}`;
}

function inferWorkflowStage(run: RunMeta | null): string {
  if (!run) {
    return "input";
  }

  if (run.status === "queued") {
    return "input";
  }

  const message = run.message.toLowerCase();
  if (message.includes("report")) {
    return "report";
  }
  if (message.includes("evaluat")) {
    return "evaluation";
  }
  if (message.includes("diagram")) {
    return "diagram";
  }
  if (message.includes("formula")) {
    return "formula";
  }
  if (message.includes("ocr")) {
    return "ocr";
  }
  if (run.status === "completed") {
    return "report";
  }
  return "input";
}

function getRunElapsedSeconds(run: RunMeta | null): number | null {
  if (!run) {
    return null;
  }

  if (run.elapsed_seconds !== null && run.elapsed_seconds !== undefined) {
    return run.elapsed_seconds;
  }

  const startedAt = run.started_at || run.created_at;
  if (!startedAt) {
    return null;
  }

  const parsed = new Date(startedAt).getTime();
  if (Number.isNaN(parsed)) {
    return null;
  }

  return Math.max((Date.now() - parsed) / 1000, 0);
}

function getStepsPerMinute(run: RunMeta | null): string {
  const elapsedSeconds = getRunElapsedSeconds(run);
  if (!run || !elapsedSeconds || run.current_step === 0) {
    return "0.00 steps/min";
  }

  const speed = (run.current_step / elapsedSeconds) * 60;
  return `${speed.toFixed(2)} steps/min`;
}

function getWorkflowBlocks(run: RunMeta | null): Array<WorkflowBlock & { state: string }> {
  const activeStage = inferWorkflowStage(run);
  const activeIndex = WORKFLOW_BLOCKS.findIndex((block) => block.key === activeStage);
  const engine = run?.engine ?? "SBERT";

  return WORKFLOW_BLOCKS.map((block, index) => {
    if (block.key === "formula" && engine !== "SBERT") {
      return { ...block, state: "skipped" };
    }
    if (run?.status === "completed") {
      return { ...block, state: "done" };
    }
    if (index < activeIndex) {
      return { ...block, state: "done" };
    }
    if (index === activeIndex) {
      return { ...block, state: run ? "active" : "pending" };
    }
    return { ...block, state: "pending" };
  });
}

async function readApiPayload<T>(response: Response): Promise<T | { detail?: string }> {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T | { detail?: string };
  }

  const text = await response.text();
  return { detail: text || `Request failed with status ${response.status}.` };
}

export default function EvaluatePage() {
  const [idealPdf, setIdealPdf] = useState<File | null>(null);
  const [rubricJson, setRubricJson] = useState<File | null>(null);
  const [studentPdfs, setStudentPdfs] = useState<File[]>([]);
  const [engine, setEngine] = useState("SBERT");
  const [ocrBackend, setOcrBackend] = useState("easyocr");
  const [azureEndpoint, setAzureEndpoint] = useState("");
  const [azureKey, setAzureKey] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentRun, setCurrentRun] = useState<RunMeta | null>(null);
  const [runHistory, setRunHistory] = useState<RunSummary[]>([]);
  const [runtimeConfig, setRuntimeConfig] = useState<RuntimeConfig | null>(null);
  const [isHostedDeployment, setIsHostedDeployment] = useState(false);
  const hostedUsesSynchronousRuns = isHostedDeployment;

  const requiresAzure = useMemo(() => ocrBackend === "azure", [ocrBackend]);
  const needsManualAzureSecrets = requiresAzure && !runtimeConfig?.azure_configured;
  const isPolling = currentRun ? ["queued", "running"].includes(currentRun.status) : false;
  const workflowBlocks = useMemo(() => getWorkflowBlocks(currentRun), [currentRun]);
  const currentElapsed = useMemo(() => getRunElapsedSeconds(currentRun), [currentRun]);

  const lastCompletedRun = useMemo(
    () => runHistory.find((run) => run.status === "completed") ?? null,
    [runHistory]
  );

  const bestRecentRun = useMemo(() => {
    return runHistory
      .filter((run) => typeof run.top_percentage === "number")
      .sort((left, right) => (right.top_percentage ?? 0) - (left.top_percentage ?? 0))[0] ?? null;
  }, [runHistory]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const hostname = window.location.hostname.toLowerCase();
    setIsHostedDeployment(!["localhost", "127.0.0.1"].includes(hostname));
  }, []);

  useEffect(() => {
    async function loadHistory() {
      try {
        const [historyResponse, runtimeResponse] = await Promise.all([
          fetch(`${BROWSER_API_BASE_URL}/jobs`, { cache: "no-store" }),
          fetch(`${BROWSER_API_BASE_URL}/runtime-config`, { cache: "no-store" }),
        ]);

        if (!historyResponse.ok) {
          throw new Error("Unable to load recent runs.");
        }

        const data = (await readApiPayload<RunSummary[]>(historyResponse)) as RunSummary[];
        setRunHistory(data);

        if (runtimeResponse.ok) {
          const runtimeData = (await readApiPayload<RuntimeConfig>(runtimeResponse)) as RuntimeConfig;
          setRuntimeConfig(runtimeData);
        }
      } catch (historyError) {
        setError(
          historyError instanceof Error
            ? historyError.message
            : "Unable to load recent runs right now."
        );
      } finally {
        setIsHistoryLoading(false);
      }
    }

    void loadHistory();
  }, []);

  useEffect(() => {
    if (!currentRun || !["queued", "running"].includes(currentRun.status) || hostedUsesSynchronousRuns) {
      return undefined;
    }

    const activeRunId = currentRun.run_id;
    const timer = window.setTimeout(() => {
      async function refreshRun() {
        try {
          const [runResponse, jobsResponse] = await Promise.all([
            fetch(`${BROWSER_API_BASE_URL}/jobs/${activeRunId}`, { cache: "no-store" }),
            fetch(`${BROWSER_API_BASE_URL}/jobs`, { cache: "no-store" }),
          ]);

          if (!runResponse.ok) {
            throw new Error("Unable to refresh the active run.");
          }

          const runData = (await readApiPayload<RunMeta>(runResponse)) as RunMeta;
          setCurrentRun(runData);

          if (jobsResponse.ok) {
            const historyData = (await readApiPayload<RunSummary[]>(jobsResponse)) as RunSummary[];
            setRunHistory(historyData);
          }
        } catch (pollError) {
          setError(
            pollError instanceof Error
              ? pollError.message
              : "Unable to refresh live job progress."
          );
        }
      }

      void refreshRun();
    }, 2200);

    return () => window.clearTimeout(timer);
  }, [currentRun, hostedUsesSynchronousRuns]);

  async function refreshHistory() {
    setIsHistoryLoading(true);
    try {
      const response = await fetch(`${BROWSER_API_BASE_URL}/jobs`, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Unable to refresh recent runs.");
      }
      const data = (await readApiPayload<RunSummary[]>(response)) as RunSummary[];
      setRunHistory(data);
    } catch (historyError) {
      setError(
        historyError instanceof Error
          ? historyError.message
          : "Unable to refresh recent runs right now."
      );
    } finally {
      setIsHistoryLoading(false);
    }
  }

  async function openRun(runId: string) {
    setError("");

    try {
      const response = await fetch(`${BROWSER_API_BASE_URL}/runs/${runId}`, { cache: "no-store" });
      const data = await readApiPayload<RunMeta>(response);
      if (!response.ok) {
        throw new Error("detail" in data && data.detail ? data.detail : "Unable to load the selected run.");
      }
      setCurrentRun(data as RunMeta);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Unable to load the selected run.");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (!idealPdf || !rubricJson || studentPdfs.length === 0) {
      setError("Please upload the ideal sheet, rubric JSON, and at least one student PDF.");
      return;
    }

    if (needsManualAzureSecrets && (!azureEndpoint || !azureKey)) {
      setError("Azure handwritten OCR requires both endpoint and key.");
      return;
    }

    const effectiveEngine = engine;
    const effectiveOcrBackend = ocrBackend;

    const formData = new FormData();
    formData.append("ideal_pdf", idealPdf);
    formData.append("rubric_json", rubricJson);
    studentPdfs.forEach((file) => formData.append("student_pdfs", file));
    formData.append("engine", effectiveEngine);
    formData.append("ocr_backend", effectiveOcrBackend);
    if (needsManualAzureSecrets) {
      formData.append("azure_endpoint", azureEndpoint);
      formData.append("azure_key", azureKey);
    }

    try {
      setIsSubmitting(true);

      const endpoint = hostedUsesSynchronousRuns ? "/evaluate" : "/jobs";

      if (hostedUsesSynchronousRuns) {
        const now = new Date().toISOString();
        setCurrentRun({
          run_id: "live-run",
          status: "running",
          engine: effectiveEngine,
          ocr_backend: effectiveOcrBackend,
          student_count: studentPdfs.length,
          created_at: now,
          started_at: now,
          completed_at: null,
          current_step: 0,
          total_steps: 0,
          progress_percent: 0,
          message: "Cloud evaluation is running synchronously. Please wait for the final result.",
          events: [
            {
              timestamp: now,
              message: "Synchronous cloud evaluation started.",
            },
          ],
          elapsed_seconds: null,
          eval_dir: null,
          report_dir: null,
          summary_rows: [],
          reports: [],
          error: null,
        });
      } else {
        setCurrentRun(null);
      }

      const response = await fetch(`${BROWSER_API_BASE_URL}${endpoint}`, {
        method: "POST",
        body: formData,
      });

      const data = await readApiPayload<RunMeta>(response);
      if (!response.ok) {
        throw new Error("detail" in data && data.detail ? data.detail : "Evaluation failed.");
      }

      setCurrentRun(data as RunMeta);
      await refreshHistory();
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Something went wrong while creating the evaluation job."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  const currentTopStudent = currentRun?.summary_rows[0] ?? null;

  return (
    <>
      <SectionShell
        title="Evaluation Command Center"
        subtitle="Configure a batch, run the multimodal grading pipeline, and follow each connected stage live from OCR to final report generation."
      >
        <div className="results-grid">
          <div className="metric-card">
            <span>Total Recorded Runs</span>
            <strong>{runHistory.length}</strong>
          </div>
          <div className="metric-card">
            <span>Active Queue State</span>
            <strong>{currentRun ? currentRun.status.toUpperCase() : "IDLE"}</strong>
          </div>
          <div className="metric-card">
            <span>Last Completed Run</span>
            <strong>{lastCompletedRun ? formatDuration(lastCompletedRun.elapsed_seconds) : "No run yet"}</strong>
          </div>
          <div className="metric-card">
            <span>Best Recent Score</span>
            <strong>
              {bestRecentRun?.top_student
                ? `${bestRecentRun.top_student} (${bestRecentRun.top_percentage?.toFixed(2)}%)`
                : "Waiting for data"}
            </strong>
          </div>
        </div>

        <form className="two-column" onSubmit={handleSubmit}>
          <div className="section-shell" style={{ marginTop: 0 }}>
            <div className="section-shell__header">
              <h2>Launch A New Run</h2>
              <p>Choose the files and execution mode. The backend will create a run ID and handle the pipeline in the background.</p>
            </div>
            <div className="form-grid">
              <label>
                <span className="field-label">Ideal Answer Sheet (PDF)</span>
                <input
                  className="file-control"
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setIdealPdf(e.target.files?.[0] || null)}
                />
              </label>

              <label>
                <span className="field-label">Rubric JSON</span>
                <input
                  className="file-control"
                  type="file"
                  accept=".json"
                  onChange={(e) => setRubricJson(e.target.files?.[0] || null)}
                />
              </label>

              <label>
                <span className="field-label">Student Answer Sheets</span>
                <input
                  className="file-control"
                  type="file"
                  accept=".pdf"
                  multiple
                  onChange={(e) => setStudentPdfs(Array.from(e.target.files || []))}
                />
                <div className="field-help">{studentPdfs.length} student file(s) ready for upload.</div>
              </label>

              <label>
                <span className="field-label">Evaluation Engine</span>
                <select
                  className="select-control"
                  value={engine}
                  onChange={(e) => setEngine(e.target.value)}
                >
                  <option value="SBERT">SBERT (fast, local)</option>
                  <option value="LLM">Gemini 2.5 Flash (LLM API)</option>
                </select>
              </label>

              <label>
                <span className="field-label">OCR Mode</span>
                <select
                  className="select-control"
                  value={ocrBackend}
                  onChange={(e) => setOcrBackend(e.target.value)}
                >
                  <option value="easyocr">Current / printed sheets (EasyOCR)</option>
                  <option value="azure">Handwritten sheets (Azure Document Intelligence)</option>
                </select>
              </label>

              {isHostedDeployment ? (
                <div className="status-card">
                  <strong>Hosted mode keeps the production backend path stable.</strong>
                  The deployed website still runs evaluation through the production backend, but
                  you can now switch OCR and evaluation engines directly from this interface.
                </div>
              ) : null}

              {requiresAzure && runtimeConfig?.azure_configured ? (
                <div className="status-card">
                  <strong>Server-managed handwritten OCR is active.</strong>
                  The deployed backend already has the handwritten OCR credentials it needs, so
                  handwritten evaluation can run without exposing secrets in the web UI.
                </div>
              ) : null}

              {isHostedDeployment && !requiresAzure ? (
                <div className="status-card">
                  <strong>Printed OCR is enabled on the hosted backend.</strong>
                  EasyOCR and SBERT remain available in production, so you can test the same
                  printed-sheet flow from the web interface.
                </div>
              ) : null}

              {requiresAzure && engine === "LLM" && runtimeConfig && !runtimeConfig.gemini_configured ? (
                <div className="status-card status-card--error">
                  Gemini mode is selected, but the backend does not currently have a
                  `GEMINI_API_KEY` configured.
                </div>
              ) : null}

              {needsManualAzureSecrets ? (
                <>
                  <label>
                    <span className="field-label">Azure Endpoint</span>
                    <input
                      className="input-control"
                      value={azureEndpoint}
                      onChange={(e) => setAzureEndpoint(e.target.value)}
                      placeholder="https://your-resource.cognitiveservices.azure.com/"
                    />
                  </label>

                  <label>
                    <span className="field-label">Azure Key</span>
                    <input
                      className="input-control"
                      type="password"
                      value={azureKey}
                      onChange={(e) => setAzureKey(e.target.value)}
                      placeholder="Paste the Azure key here"
                    />
                  </label>
                </>
              ) : null}

              <div className="inline-actions">
                <button className="button-primary" type="submit" disabled={isSubmitting || isPolling}>
                  {isSubmitting ? "Creating Job..." : isPolling ? "Job Running..." : "Launch Evaluation Job"}
                </button>
                <button className="button-secondary" type="button" onClick={() => void refreshHistory()}>
                  Refresh History
                </button>
              </div>
            </div>
          </div>

          <div className="section-shell" style={{ marginTop: 0 }}>
            <div className="section-shell__header">
              <h2>Live Workflow</h2>
              <p>Watch the connected pipeline blocks update in sequence while the job runs.</p>
            </div>

            {currentRun ? (
              <div className="monitor-stack">
                <div className="status-row">
                  <span className={getStatusTone(currentRun.status)}>{currentRun.status.toUpperCase()}</span>
                  <span className="pill">{getEngineLabel(currentRun.engine)}</span>
                  <span className="pill">{getOcrLabel(currentRun.ocr_backend)}</span>
                </div>

                <div className="workflow-monitor">
                  <div className="workflow-monitor__head">
                    <div>
                      <strong>{currentRun.message}</strong>
                      <span>Run ID {currentRun.run_id}</span>
                    </div>
                    <div className="workflow-monitor__stats">
                      <span>{currentRun.progress_percent}% complete</span>
                      <span>{formatDuration(currentElapsed)}</span>
                      <span>{getStepsPerMinute(currentRun)}</span>
                    </div>
                  </div>

                  <div className="workflow-diagram">
                    {workflowBlocks.map((block, index) => (
                      <div className="workflow-diagram__segment" key={block.key}>
                        <article className={`workflow-block workflow-block--${block.state}`}>
                          <div className="workflow-block__top">
                            <span className="workflow-block__index">{index + 1}</span>
                            <span className="workflow-block__state">{block.state}</span>
                          </div>
                          <h3>{block.title}</h3>
                          <p>{block.detail}</p>
                        </article>
                        {index < workflowBlocks.length - 1 ? <div className="workflow-connector" /> : null}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="progress-shell">
                  <div className="progress-meta">
                    <strong>
                      Step {currentRun.current_step} of {currentRun.total_steps || "?"}
                    </strong>
                    <span>{currentRun.progress_percent}% complete</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${Math.max(currentRun.progress_percent, 4)}%` }} />
                  </div>
                </div>

                {currentRun.error ? <div className="status-card status-card--error">{currentRun.error}</div> : null}

                <div>
                  <div className="field-label">Execution Timeline</div>
                  <div className="event-list">
                    {currentRun.events.slice().reverse().map((item) => (
                      <div className="event-item" key={`${item.timestamp}-${item.message}`}>
                        <strong>{formatTimestamp(item.timestamp)}</strong>
                        <span>{item.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <strong>No active run selected.</strong>
                <span>Create a new job to activate the live workflow diagram and stage monitor.</span>
              </div>
            )}
          </div>
        </form>

        {error ? <div className="status-card status-card--error">{error}</div> : null}
      </SectionShell>

      {currentRun && currentRun.summary_rows.length > 0 ? (
        <SectionShell
          title="Run Results"
          subtitle={`Opened run ${currentRun.run_id}. Review ranking, summary metrics, and download the generated reports.`}
        >
          <div className="results-grid">
            <div className="metric-card">
              <span>Students Processed</span>
              <strong>{currentRun.summary_rows.length}</strong>
            </div>
            <div className="metric-card">
              <span>Average Score</span>
              <strong>{getAveragePercentage(currentRun.summary_rows)}</strong>
            </div>
            <div className="metric-card">
              <span>Top Performer</span>
              <strong>
                {currentTopStudent
                  ? `${currentTopStudent.student} (${currentTopStudent.percentage.toFixed(2)}%)`
                  : "Not available"}
              </strong>
            </div>
            <div className="metric-card">
              <span>Total Processing Time</span>
              <strong>{formatDuration(currentRun.elapsed_seconds)}</strong>
            </div>
          </div>

          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Student</th>
                  <th>Total Score</th>
                  <th>Max Score</th>
                  <th>Percentage</th>
                  <th>Report</th>
                </tr>
              </thead>
              <tbody>
                {currentRun.summary_rows.map((row) => {
                  const report = currentRun.reports.find((item) => item.student === row.student);
                  return (
                    <tr key={row.student}>
                      <td>{row.rank}</td>
                      <td>{row.student}</td>
                      <td>{row.total_score}</td>
                      <td>{row.max_score}</td>
                      <td>{row.percentage}%</td>
                      <td>
                        {report ? (
                          <a
                            className="link-chip"
                            href={`${BROWSER_API_BASE_URL}${report.download_url.replace(/^\/api/, "")}`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Download PDF
                          </a>
                        ) : (
                          "Pending"
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </SectionShell>
      ) : null}

      <SectionShell
        title="Recent Run History"
        subtitle="Reopen earlier evaluations, compare engines and OCR modes, and keep your testing workflow traceable as the dataset grows."
      >
        {isHistoryLoading ? (
          <div className="empty-state">
            <strong>Loading runs...</strong>
            <span>The API is collecting previously saved evaluations.</span>
          </div>
        ) : runHistory.length ? (
          <div className="run-history-grid">
            {runHistory.map((run) => (
              <div className="run-history-card" key={run.run_id}>
                <div className="status-row">
                  <span className={getStatusTone(run.status)}>{run.status.toUpperCase()}</span>
                  <span className="pill">{getEngineLabel(run.engine)}</span>
                </div>

                <h3>{run.run_id}</h3>

                <div className="history-meta">
                  <span>{getOcrLabel(run.ocr_backend)}</span>
                  <span>{run.student_count} student(s)</span>
                  <span>Created {formatTimestamp(run.created_at)}</span>
                  <span>Duration {formatDuration(run.elapsed_seconds)}</span>
                </div>

                <div className="history-highlight">
                  <strong>{run.top_student ? run.top_student : "No score yet"}</strong>
                  <span>
                    {run.top_percentage !== null && run.top_percentage !== undefined
                      ? `${run.top_percentage.toFixed(2)}% top score`
                      : run.message}
                  </span>
                </div>

                <button className="button-secondary" type="button" onClick={() => void openRun(run.run_id)}>
                  Open This Run
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <strong>No saved runs yet.</strong>
            <span>Your first evaluation job will appear here automatically.</span>
          </div>
        )}
      </SectionShell>
    </>
  );
}
