import { SectionShell } from "../../components/section-shell";
import { fetchJson } from "../../lib/api";
import { fallbackTeam } from "../../lib/fallback-data";

type TeamMember = {
  name: string;
  branch: string;
  role: string;
  photo: string;
  linkedin: string;
  email: string;
};

const teamMetrics = [
  { label: "Core Members", value: "4" },
  { label: "Focus", value: "AI + OCR" },
  { label: "Mode", value: "BTP Product Build" },
];

export default async function TeamPage() {
  const team = await fetchJson<TeamMember[]>("/api/team", fallbackTeam);

  return (
    <>
      <SectionShell
        title="Team"
        subtitle="The product is being shaped by a focused academic team combining AI, evaluation logic, interface design, and faculty guidance."
      >
        <div className="team-hero">
          <div className="team-hero__copy">
            <span className="hero-chip">Project Contributors</span>
            <h3>Built as a collaborative BTP platform, not just a one-off grading demo.</h3>
            <p>
              The team is working across OCR, multimodal evaluation, formula understanding,
              product UI, documentation, and faculty-ready reporting.
            </p>
          </div>
          <div className="team-stat-grid">
            {teamMetrics.map((item) => (
              <article key={item.label} className="team-stat-card">
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </article>
            ))}
          </div>
        </div>
      </SectionShell>

      <SectionShell
        title="People Behind The Platform"
        subtitle="Each profile highlights the person, role, branch, and quick access links for collaboration."
      >
        <div className="team-grid">
          {team.map((member, index) => (
            <article key={member.name} className={`team-card team-card--accent-${(index % 4) + 1}`}>
              <div className="team-card__media">
                <img src={member.photo} alt={member.name} />
                <span className="team-role-badge">{member.role}</span>
              </div>
              <div className="team-card__body">
                <h3>{member.name}</h3>
                <div className="team-branch">{member.branch}</div>
                <p>
                  Contributing to the multimodal subjective grading platform with a focus on
                  research execution, system development, and product presentation.
                </p>
                <div className="link-row">
                  <a className="link-chip" href={member.linkedin} target="_blank" rel="noreferrer">
                    LinkedIn
                  </a>
                  <a className="link-chip" href={member.email}>
                    Email
                  </a>
                </div>
              </div>
            </article>
          ))}
        </div>
      </SectionShell>
    </>
  );
}
