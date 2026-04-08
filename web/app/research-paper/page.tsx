"use client";

import { ChangeEvent, useState } from "react";
import { SectionShell } from "../../components/section-shell";

export default function ResearchPaperPage() {
  const [paperUrl, setPaperUrl] = useState<string | null>(null);
  const [paperName, setPaperName] = useState("No paper uploaded");

  function handlePaperChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      setPaperUrl(null);
      setPaperName("No paper uploaded");
      return;
    }
    setPaperName(file.name);
    setPaperUrl(URL.createObjectURL(file));
  }

  return (
    <>
      <SectionShell
        title="Research Paper"
        subtitle="Upload and preview your paper here while the final storage flow is being prepared."
      >
        <div className="two-column">
          <div className="section-shell" style={{ marginTop: 0 }}>
            <div className="section-shell__header">
              <h2>Paper Preview Workspace</h2>
              <p>
                This page already supports local PDF preview in the website. Later we can connect it
                to backend storage or a publication repository.
              </p>
            </div>
            <div className="form-grid">
              <label>
                <span className="field-label">Upload Research Paper PDF</span>
                <input className="file-control" type="file" accept=".pdf" onChange={handlePaperChange} />
              </label>
              <div className="status-card">
                <strong>Current file:</strong> {paperName}
              </div>
            </div>
          </div>

          <div className="section-shell" style={{ marginTop: 0 }}>
            <div className="section-shell__header">
              <h2>What This Tab Will Support</h2>
              <p>
                Final paper preview, downloadable PDF, abstract summary, publication metadata, and
                later external links to arXiv, IEEE, or institutional repositories.
              </p>
            </div>
          </div>
        </div>
      </SectionShell>

      <SectionShell
        title="PDF Preview"
        subtitle="Once a paper is uploaded, the embedded preview appears below."
      >
        <div className="upload-preview">
          {paperUrl ? (
            <iframe src={paperUrl} title="Research Paper Preview" />
          ) : (
            <div className="status-card">Upload a PDF to preview it here.</div>
          )}
        </div>
      </SectionShell>
    </>
  );
}
