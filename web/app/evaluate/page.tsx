"use client";

import { FormEvent, SVGProps, useEffect, useMemo, useState } from "react";
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

type QuestionResult = {
  question_id: string;
  score: number;
  max_marks: number;
};

type StudentResult = {
  student_base: string;
  total_score: number;
  max_total: number;
  percentage: number;
  questions: QuestionResult[];
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
  results: StudentResult[];
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
  google_vision_supported: boolean;
  gemini_configured: boolean;
  durable_run_storage: boolean;
  allowed_origins: string[];
  easyocr_use_gpu?: boolean;
  max_parallel_pipelines?: number;
  formula_autoskip_enabled?: boolean;
};

type UploadSessionResponse = {
  session_id: string;
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
    detail: "EasyOCR, Google Vision AI, or Azure Document Intelligence",
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

function IconHistory(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M4 12a8 8 0 1 0 2.35-5.65" />
      <path d="M4 4v4h4" />
      <path d="M12 8v5l3 2" />
    </svg>
  );
}

function IconDownload(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M12 4v10" />
      <path d="m8 10 4 4 4-4" />
      <path d="M5 19h14" />
    </svg>
  );
}

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
  return engine === "LLM" ? "Gemini 2.5 Flash (Vertex AI)" : "SBERT (fast, local)";
}

function getOcrLabel(ocrBackend: string): string {
  if (ocrBackend === "google_vision") {
    return "Handwritten sheets (Google Vision AI)";
  }
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

function roundMarks(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

function buildQuestionwiseRows(results: StudentResult[]): Array<Record<string, string>> {
  const questionIds = Array.from(
    new Set(results.flatMap((result) => result.questions.map((question) => question.question_id)))
  ).sort((left, right) => {
    const leftNumber = Number.parseInt(left.replace(/\D+/g, ""), 10);
    const rightNumber = Number.parseInt(right.replace(/\D+/g, ""), 10);

    if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber) && leftNumber !== rightNumber) {
      return leftNumber - rightNumber;
    }

    return left.localeCompare(right);
  });

  return results.map((result) => {
    const row: Record<string, string> = {
      Student: result.student_base,
    };

    questionIds.forEach((questionId) => {
      const question = result.questions.find((item) => item.question_id === questionId);
      row[questionId] = question ? `${roundMarks(question.score)} / ${roundMarks(question.max_marks)}` : "--";
    });

    row.Total = `${roundMarks(result.total_score)} / ${roundMarks(result.max_total)}`;
    return row;
  });
}

function downloadCsv(filename: string, rows: Array<Record<string, string>>) {
  if (!rows.length || typeof window === "undefined") {
    return;
  }

  const headers = Object.keys(rows[0]);
  const escapeCell = (value: string) => `"${value.replace(/"/g, '""')}"`;
  const csv = [
    headers.join(","),
    ...rows.map((row) => headers.map((header) => escapeCell(row[header] ?? "")).join(",")),
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
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
  if (message.includes("formula parsing not needed") || message.includes("no formula cues")) {
    return "diagram";
  }
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

function formulaMarkedNotNeeded(run: RunMeta | null): boolean {
  if (!run) {
    return false;
  }

  const messages = [run.message, ...run.events.map((event) => event.message)].map((value) => value.toLowerCase());
  return messages.some(
    (message) => message.includes("formula parsing not needed") || message.includes("no formula cues")
  );
}

function getWorkflowBlocks(run: RunMeta | null): Array<WorkflowBlock & { state: string }> {
  const activeStage = inferWorkflowStage(run);
  const activeIndex = WORKFLOW_BLOCKS.findIndex((block) => block.key === activeStage);
  const formulaNotNeeded = formulaMarkedNotNeeded(run);

  return WORKFLOW_BLOCKS.map((block, index) => {
    if (block.key === "formula" && formulaNotNeeded) {
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

function getSubmissionErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    if (error.message === "Failed to fetch") {
      return "The upload request could not reach the backend. Please retry. Large hosted batches are now uploaded file-by-file, so this should be much less likely.";
    }
    return error.message;
  }

  return "Something went wrong while creating the evaluation job.";
}

function getResponseDetail(data: unknown): string | undefined {
  if (!data || typeof data !== "object" || !("detail" in data)) {
    return undefined;
  }

  const detail = (data as { detail?: unknown }).detail;
  return typeof detail === "string" && detail.trim() ? detail : undefined;
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
  const [submitStatus, setSubmitStatus] = useState("");
  const [currentRun, setCurrentRun] = useState<RunMeta | null>(null);
  const [runHistory, setRunHistory] = useState<RunSummary[]>([]);
  const [historyRunDetails, setHistoryRunDetails] = useState<Record<string, RunMeta>>({});
  const [historyLoadState, setHistoryLoadState] = useState<Record<string, "idle" | "loading" | "error">>({});
  const [historyLoadErrors, setHistoryLoadErrors] = useState<Record<string, string>>({});
  const [runtimeConfig, setRuntimeConfig] = useState<RuntimeConfig | null>(null);
  const [isHostedDeployment, setIsHostedDeployment] = useState(false);

  const requiresAzure = useMemo(() => ocrBackend === "azure", [ocrBackend]);
  const needsManualAzureSecrets = requiresAzure && !runtimeConfig?.azure_configured;
  const isPolling = currentRun ? ["queued", "running"].includes(currentRun.status) : false;
  const shouldUseUploadSessions = isHostedDeployment && (runtimeConfig?.durable_run_storage ?? true);
  const hostedUsesSynchronousRuns = false;
  const workflowBlocks = useMemo(() => getWorkflowBlocks(currentRun), [currentRun]);
  const currentElapsed = useMemo(() => getRunElapsedSeconds(currentRun), [currentRun]);
  const questionwiseRows = useMemo(
    () => (currentRun?.results?.length ? buildQuestionwiseRows(currentRun.results) : []),
    [currentRun]
  );

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
          console.error("Unable to refresh live job progress.", pollError);
        }
      }

      void refreshRun();
    }, 2200);

    return () => window.clearTimeout(timer);
  }, [currentRun, hostedUsesSynchronousRuns]);

  async function refreshHistory(options?: { silent?: boolean }) {
    setIsHistoryLoading(true);
    try {
      const response = await fetch(`${BROWSER_API_BASE_URL}/jobs`, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Unable to refresh recent runs.");
      }
      const data = (await readApiPayload<RunSummary[]>(response)) as RunSummary[];
      setRunHistory(data);
    } catch (historyError) {
      if (!options?.silent) {
        setError(
          historyError instanceof Error
            ? historyError.message
            : "Unable to refresh recent runs right now."
        );
      }
    } finally {
      setIsHistoryLoading(false);
    }
  }

  async function openRun(runId: string) {
    setError("");

    try {
      const runData = await loadRunDetails(runId);
      setCurrentRun(runData);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Unable to load the selected run.");
    }
  }

  async function loadRunDetails(runId: string): Promise<RunMeta> {
    const cached = historyRunDetails[runId];
    if (cached) {
      return cached;
    }

    setHistoryLoadState((current) => ({ ...current, [runId]: "loading" }));
    setHistoryLoadErrors((current) => ({ ...current, [runId]: "" }));

    try {
      const response = await fetch(`${BROWSER_API_BASE_URL}/runs/${runId}`, { cache: "no-store" });
      const data = await readApiPayload<RunMeta>(response);
      if (!response.ok) {
        throw new Error("detail" in data && data.detail ? data.detail : "Unable to load the selected run.");
      }

      const runData = data as RunMeta;
      setHistoryRunDetails((current) => ({ ...current, [runId]: runData }));
      setHistoryLoadState((current) => ({ ...current, [runId]: "idle" }));
      return runData;
    } catch (detailsError) {
      const message =
        detailsError instanceof Error ? detailsError.message : "Unable to load run history right now.";
      setHistoryLoadState((current) => ({ ...current, [runId]: "error" }));
      setHistoryLoadErrors((current) => ({ ...current, [runId]: message }));
      throw detailsError;
    }
  }

  async function handleHistoryToggle(runId: string, open: boolean) {
    if (!open || historyRunDetails[runId] || historyLoadState[runId] === "loading") {
      return;
    }

    try {
      await loadRunDetails(runId);
    } catch (detailsError) {
      console.error("Unable to load saved run history.", detailsError);
    }
  }

  async function createUploadSession(): Promise<string> {
    const response = await fetch(`${BROWSER_API_BASE_URL}/upload-sessions`, {
      method: "POST",
    });
    const data = await readApiPayload<UploadSessionResponse>(response);
    if (!response.ok) {
      throw new Error(getResponseDetail(data) ?? "Unable to create the upload session.");
    }
    return (data as UploadSessionResponse).session_id;
  }

  async function uploadSessionFile(
    sessionId: string,
    kind: "ideal_pdf" | "rubric_json" | "student_pdf",
    file: File
  ): Promise<void> {
    const formData = new FormData();
    formData.append("kind", kind);
    formData.append("file", file);

    const response = await fetch(`${BROWSER_API_BASE_URL}/upload-sessions/${sessionId}/files`, {
      method: "POST",
      body: formData,
    });
    const data = await readApiPayload<Record<string, unknown>>(response);
    if (!response.ok) {
      throw new Error(getResponseDetail(data) ?? `Unable to upload ${file.name}.`);
    }
  }

  async function createJobFromUploadSession(
    sessionId: string,
    effectiveEngine: string,
    effectiveOcrBackend: string
  ): Promise<RunMeta> {
    const formData = new FormData();
    formData.append("engine", effectiveEngine);
    formData.append("ocr_backend", effectiveOcrBackend);
    if (needsManualAzureSecrets) {
      formData.append("azure_endpoint", azureEndpoint);
      formData.append("azure_key", azureKey);
    }

    const response = await fetch(`${BROWSER_API_BASE_URL}/upload-sessions/${sessionId}/jobs`, {
      method: "POST",
      body: formData,
    });
    const data = await readApiPayload<RunMeta>(response);
    if (!response.ok) {
      throw new Error(getResponseDetail(data) ?? "Evaluation failed.");
    }
    return data as RunMeta;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSubmitStatus("");

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

    try {
      setIsSubmitting(true);
      let createdRun: RunMeta;

      if (shouldUseUploadSessions) {
        setSubmitStatus("Creating an upload session...");
        const sessionId = await createUploadSession();
        const now = new Date().toISOString();
        setCurrentRun({
          run_id: sessionId,
          status: "running",
          engine: effectiveEngine,
          ocr_backend: effectiveOcrBackend,
          student_count: studentPdfs.length,
          created_at: now,
          started_at: now,
          completed_at: null,
          current_step: 1,
          total_steps: WORKFLOW_BLOCKS.length,
          progress_percent: 6,
          message: "Upload session created. Preparing files for the cloud run.",
          events: [
            {
              timestamp: now,
              message: "Upload session created.",
            },
          ],
          elapsed_seconds: null,
          eval_dir: null,
          report_dir: null,
          summary_rows: [],
          reports: [],
          results: [],
          error: null,
        });

        const uploadQueue: Array<{
          kind: "ideal_pdf" | "rubric_json" | "student_pdf";
          file: File;
          label: string;
        }> = [
          { kind: "ideal_pdf", file: idealPdf, label: "ideal answer sheet" },
          { kind: "rubric_json", file: rubricJson, label: "rubric JSON" },
          ...studentPdfs.map((file, index) => ({
            kind: "student_pdf" as const,
            file,
            label: `student sheet ${index + 1} of ${studentPdfs.length}`,
          })),
        ];

        for (const [index, item] of uploadQueue.entries()) {
          setSubmitStatus(`Uploading ${item.label} (${index + 1}/${uploadQueue.length})...`);
          setCurrentRun((current) =>
            current
              ? {
                  ...current,
                  message: `Uploading ${item.label} (${index + 1}/${uploadQueue.length})...`,
                  progress_percent: Math.min(18 + Math.round(((index + 1) / uploadQueue.length) * 18), 36),
                  events: [
                    ...current.events,
                    {
                      timestamp: new Date().toISOString(),
                      message: `Uploaded ${item.label}.`,
                    },
                  ].slice(-20),
                }
              : current
          );
          await uploadSessionFile(sessionId, item.kind, item.file);
        }

        setSubmitStatus("All files uploaded. Starting the background evaluation...");
        setCurrentRun((current) =>
          current
            ? {
                ...current,
                message: "Files uploaded. Starting the background evaluation...",
                progress_percent: 40,
                events: [
                  ...current.events,
                  {
                    timestamp: new Date().toISOString(),
                    message: "Files validated and submitted to the background pipeline.",
                  },
                ].slice(-20),
              }
            : current
        );
        createdRun = await createJobFromUploadSession(sessionId, effectiveEngine, effectiveOcrBackend);
      } else {
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
            current_step: 1,
            total_steps: WORKFLOW_BLOCKS.length,
            progress_percent: 8,
            message: "Inputs received. Preparing OCR extraction.",
            events: [
              {
                timestamp: now,
                message: "Synchronous cloud evaluation started.",
              },
              {
                timestamp: now,
                message: "Files validated and queued for processing.",
              },
            ],
            elapsed_seconds: null,
            eval_dir: null,
            report_dir: null,
            summary_rows: [],
            reports: [],
            results: [],
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

        createdRun = data as RunMeta;
      }

      setCurrentRun(createdRun);
      setSubmitStatus("");
      await refreshHistory({ silent: true });
    } catch (submitError) {
      setError(getSubmissionErrorMessage(submitError));
      setSubmitStatus("");
    } finally {
      setIsSubmitting(false);
    }
  }

  const currentTopStudent = currentRun?.summary_rows[0] ?? null;

  return (
    <>
      <SectionShell
        title="Evaluate Answer Sheets"
        subtitle="Upload the answer sheets, choose the scoring path, and follow the live workflow from OCR to final report generation."
      >
        <div className="results-grid">
          <div className="metric-card">
            <span>Saved Sessions</span>
            <strong>{runHistory.length}</strong>
          </div>
          <div className="metric-card">
            <span>Live Status</span>
            <strong>{currentRun ? currentRun.status.toUpperCase() : "IDLE"}</strong>
          </div>
          <div className="metric-card">
            <span>Last Run Time</span>
            <strong>{lastCompletedRun ? formatDuration(lastCompletedRun.elapsed_seconds) : "No run yet"}</strong>
          </div>
          <div className="metric-card">
            <span>Best Recent Result</span>
            <strong>
              {bestRecentRun?.top_student
                ? `${bestRecentRun.top_student} (${bestRecentRun.top_percentage?.toFixed(2)}%)`
                : "Waiting for data"}
            </strong>
          </div>
        </div>

        <form className="evaluate-layout" onSubmit={handleSubmit}>
          <div className="evaluate-panel">
            <div className="evaluate-panel__header">
              <span className="evaluate-panel__step">Step 1 · Inputs & configuration</span>
              <h3>Create a new evaluation run</h3>
              <p>
                Add the ideal sheet, rubric, and student sheets first. Then select the OCR and
                scoring path you want the pipeline to use for this run.
              </p>
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
                <div className="field-row">
                  <span className="field-label">Rubric JSON</span>
                  <a className="link-chip" href="/samples/sample-rubric.json" download>
                    <IconDownload width={14} height={14} />
                    Download sample rubric
                  </a>
                </div>
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

              <div className="evaluate-config-grid">
                <label>
                  <span className="field-label">Evaluation Engine</span>
                  <select
                    className="select-control"
                    value={engine}
                    onChange={(e) => setEngine(e.target.value)}
                  >
                    <option value="SBERT">SBERT (fast, local)</option>
                    <option value="LLM">Gemini 2.5 Flash (Vertex AI)</option>
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
                    <option value="google_vision">Handwritten sheets (Google Vision AI)</option>
                    <option value="azure">Handwritten sheets (Azure Document Intelligence)</option>
                  </select>
                </label>
              </div>

              {isHostedDeployment ? (
                <div className="status-card">
                  <strong>Hosted mode uploads first, then runs one managed cloud evaluation.</strong>
                  The deployed interface sends the files one by one, then completes the production
                  run on the backend with a bounded worker scheduler so larger handwritten workflows
                  stay more stable.
                </div>
              ) : (
                <div className="status-card">
                  <strong>Local workspace mode is active.</strong>
                  This setup is ideal for research testing, debugging, and comparing different OCR
                  or scoring paths before pushing changes live.
                </div>
              )}

              {isHostedDeployment && runtimeConfig && !runtimeConfig.durable_run_storage ? (
                <div className="status-card status-card--error">
                  Durable run storage is not configured on this deployment yet. Set
                  `API_RUNS_BUCKET` on the backend so completed runs and PDF downloads stay
                  available after Cloud Run instance changes.
                </div>
              ) : null}

              {ocrBackend === "google_vision" ? (
                <div className="status-card">
                  <strong>Google Vision AI is active for handwritten OCR.</strong>
                  This mode uses the backend&apos;s Google Cloud identity in production, and local
                  Application Default Credentials when you run the backend on your own machine.
                </div>
              ) : null}

              {engine === "LLM" && runtimeConfig?.gemini_configured ? (
                <div className="status-card">
                  <strong>Gemini on Vertex AI is ready.</strong>
                  The backend will authenticate with Google Cloud credentials instead of a
                  standalone Gemini API key, and formula parsing now runs before Gemini scoring
                  whenever formulas are detected.
                </div>
              ) : null}

              {runtimeConfig ? (
                <div className="status-card">
                  <strong>Runtime scheduler status.</strong>
                  {" "}
                  {runtimeConfig.formula_autoskip_enabled === false
                    ? "Formula auto-skip is disabled."
                    : "Formula auto-skip is enabled."}
                  {" "}
                  The backend currently allows up to {runtimeConfig.max_parallel_pipelines ?? 1} pipeline run(s) per instance.
                  {typeof runtimeConfig.easyocr_use_gpu === "boolean"
                    ? ` EasyOCR GPU mode is ${runtimeConfig.easyocr_use_gpu ? "enabled" : "disabled"} on the backend.`
                    : ""}
                </div>
              ) : null}

              {requiresAzure && runtimeConfig?.azure_configured ? (
                <div className="status-card">
                  <strong>Azure handwritten OCR is ready.</strong>
                  The backend already has the credentials it needs, so handwritten evaluation can
                  run without exposing secrets in the web interface.
                </div>
              ) : null}

              {engine === "LLM" && runtimeConfig && !runtimeConfig.gemini_configured ? (
                <div className="status-card status-card--error">
                  Gemini on Vertex AI is selected, but the backend does not currently have
                  Google Cloud Vertex AI configured. Set `GOOGLE_CLOUD_PROJECT`
                  (or `VERTEX_AI_PROJECT`) and make sure the backend identity can call
                  Vertex AI.
                </div>
              ) : null}

              {needsManualAzureSecrets ? (
                <div className="evaluate-config-grid">
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
                </div>
              ) : null}

              <div className="inline-actions">
                <button className="button-primary" type="submit" disabled={isSubmitting || isPolling}>
                  {isSubmitting ? "Creating Job..." : isPolling ? "Job Running..." : "Run Evaluation"}
                </button>
                <button className="button-secondary" type="button" onClick={() => void refreshHistory()}>
                  <IconHistory width={14} height={14} />
                  Refresh History
                </button>
              </div>
            </div>
          </div>

          <div className="evaluate-panel">
            <div className="evaluate-panel__header">
              <span className="evaluate-panel__step">Step 2 · Workflow & tracking</span>
              <h3>Live workflow tracker</h3>
              <p>
                Follow the run from input validation to report generation with a cleaner stage view
                and live progress tracker.
              </p>
            </div>

            {currentRun ? (
              <div className="monitor-stack">
                <div className="workflow-summary-card">
                  <div>
                    <span className="workflow-summary-card__label">Current stage</span>
                    <strong>{currentRun.message}</strong>
                    <span className="workflow-summary-card__label">Run ID {currentRun.run_id}</span>
                  </div>
                  <div className="workflow-summary-card__stats">
                    <span className={getStatusTone(currentRun.status)}>{currentRun.status.toUpperCase()}</span>
                    <span>{getEngineLabel(currentRun.engine)}</span>
                    <span>{getOcrLabel(currentRun.ocr_backend)}</span>
                    <span>{formatDuration(currentElapsed)}</span>
                    <span>{getStepsPerMinute(currentRun)}</span>
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

                <div className="workflow-simple-list">
                  {workflowBlocks.map((block, index) => {
                    const itemClass =
                      block.state === "pending"
                        ? "workflow-simple-item"
                        : `workflow-simple-item workflow-simple-item--${block.state}`;

                    return (
                      <article className={itemClass} key={block.key}>
                        <span className="workflow-simple-item__index">{index + 1}</span>
                        <div className="workflow-simple-item__body">
                          <strong>{block.title}</strong>
                          <span>{block.detail}</span>
                        </div>
                        <span className="workflow-simple-item__state">
                          {block.state === "skipped" ? "Not needed" : block.state}
                        </span>
                      </article>
                    );
                  })}
                </div>

                {currentRun.error ? <div className="status-card status-card--error">{currentRun.error}</div> : null}
              </div>
            ) : isSubmitting && submitStatus ? (
              <div className="empty-state">
                <strong>{submitStatus}</strong>
                <span>
                  The hosted backend uploads files one by one, then completes the cloud run in a
                  single request so larger handwritten batches do not die in a background thread.
                </span>
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
                            <IconDownload width={14} height={14} />
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

          {questionwiseRows.length ? (
            <div className="table-shell">
              <div className="table-shell__header">
                <div>
                  <h3>Question-wise marks table</h3>
                  <p>Download the full marksheet with each student&apos;s question-wise scores and total.</p>
                </div>
                <button
                  className="button-secondary"
                  type="button"
                  onClick={() => downloadCsv(`${currentRun.run_id}-questionwise-marks.csv`, questionwiseRows)}
                >
                  <IconDownload width={14} height={14} />
                  Download CSV
                </button>
              </div>
              <table>
                <thead>
                  <tr>
                    {Object.keys(questionwiseRows[0]).map((header) => (
                      <th key={header}>{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {questionwiseRows.map((row) => (
                    <tr key={row.Student}>
                      {Object.entries(row).map(([key, value]) => (
                        <td key={`${row.Student}-${key}`}>{value}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </SectionShell>
      ) : null}

      <SectionShell
        title="Recent Run History"
        subtitle="Reopen earlier evaluations, compare engines and OCR modes, and keep your testing workflow traceable as the dataset grows."
      >
        <details className="history-section-dropdown">
          <summary className="history-section-dropdown__summary">
            <span className="history-section-dropdown__label">
              <IconHistory width={15} height={15} />
              Recent runs
            </span>
            <span className="history-section-dropdown__meta">
              <span className="history-section-dropdown__hint">
                {isHistoryLoading
                  ? "Loading..."
                  : runHistory.length
                    ? `${runHistory.length} saved`
                    : "No runs"}
              </span>
              <span className="history-section-dropdown__chevron" aria-hidden="true">▾</span>
            </span>
          </summary>

          <div className="history-section-dropdown__content">
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

                    <div className="run-history-card__title">
                      <span className="run-history-card__icon">
                        <IconHistory width={15} height={15} />
                      </span>
                      <h3>{run.run_id}</h3>
                    </div>

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

                    <details
                      className="run-history-dropdown"
                      onToggle={(event) =>
                        void handleHistoryToggle(run.run_id, (event.currentTarget as HTMLDetailsElement).open)
                      }
                    >
                      <summary className="run-history-dropdown__summary">
                        <span className="run-history-dropdown__label">
                          <IconHistory width={15} height={15} />
                          Run History
                        </span>
                        <span className="run-history-dropdown__hint">View timeline</span>
                      </summary>

                      <div className="run-history-dropdown__content">
                        {historyLoadState[run.run_id] === "loading" ? (
                          <div className="run-history-dropdown__empty">Loading run history...</div>
                        ) : historyLoadState[run.run_id] === "error" ? (
                          <div className="run-history-dropdown__empty">
                            {historyLoadErrors[run.run_id] || "Unable to load run history."}
                          </div>
                        ) : historyRunDetails[run.run_id]?.events?.length ? (
                          <div className="run-history-event-list">
                            {historyRunDetails[run.run_id].events
                              .slice()
                              .reverse()
                              .map((item) => (
                                <div className="run-history-event" key={`${item.timestamp}-${item.message}`}>
                                  <strong>{formatTimestamp(item.timestamp)}</strong>
                                  <span>{item.message}</span>
                                </div>
                              ))}
                          </div>
                        ) : (
                          <div className="run-history-dropdown__empty">No run history available for this evaluation yet.</div>
                        )}
                      </div>
                    </details>

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
          </div>
        </details>
      </SectionShell>
    </>
  );
}
