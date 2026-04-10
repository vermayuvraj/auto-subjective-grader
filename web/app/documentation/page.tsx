import { readFile } from "node:fs/promises";
import path from "node:path";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const metadata = {
  title: "Documentation | Ai Grader",
  description:
    "Detailed project report for the Automated Subjective Answer Sheet Evaluation System.",
};

async function getDocumentationContent() {
  const reportPath = path.join(process.cwd(), "content", "detailed-project-report.md");
  return readFile(reportPath, "utf8");
}

export default async function DocumentationPage() {
  const markdown = await getDocumentationContent();

  return (
    <article className="paper-page documentation-report-page">
      <header className="paper-header documentation-report-header">
        <p className="paper-header__type">Project Documentation</p>
        <h1>Automated Subjective Answer Sheet Evaluation System</h1>
        <p className="paper-header__subtitle">
          This page renders the current detailed project report as a clean documentation surface.
          It is designed to open independently as your documentation experience while keeping the
          website interface focused on evaluation.
        </p>
        <div className="paper-meta">
          <span>Detailed project report</span>
          <span>Research-ready structure</span>
          <span>Docs subdomain compatible</span>
        </div>
      </header>

      <section className="documentation-report">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </section>
    </article>
  );
}
