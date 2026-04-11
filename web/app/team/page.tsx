import { fetchJson } from "../../lib/api";
import { fallbackTeam } from "../../lib/fallback-data";

type TeamMember = {
  name: string;
  branch: string;
  role: string;
  photo: string;
  linkedin: string;
  email: string;
  summary?: string;
  github?: string;
  website?: string;
};

export default async function TeamPage() {
  const team = await fetchJson<TeamMember[]>("/api/team", fallbackTeam);
  const featuredMember = team.find((member) => member.name === "Yuvraj Verma");

  return (
    <section className="team-minimal-page">
      <header className="team-minimal-header">
        <div>
          <p className="team-minimal-header__eyebrow">Project Team</p>
          <h1>People Behind The System</h1>
          <p>
            Meet the mentor and builders shaping the grading platform, from research direction to
            AI workflow design and product delivery.
          </p>
        </div>
        <div className="team-minimal-header__stats">
          <article className="team-minimal-stat">
            <span>Core contributors</span>
            <strong>{team.length}</strong>
          </article>
          <article className="team-minimal-stat">
            <span>Academic leadership</span>
            <strong>1 mentor-led team</strong>
          </article>
          <article className="team-minimal-stat">
            <span>Primary focus</span>
            <strong>AI, evaluation, and research</strong>
          </article>
          <article className="team-minimal-stat">
            <span>Featured builder</span>
            <strong>{featuredMember?.name ?? "Yuvraj Verma"}</strong>
          </article>
        </div>
      </header>

      <div className="team-grid team-grid--minimal">
        {team.map((member, index) => (
          <article
            key={member.name}
            className={`team-card team-card--accent-${(index % 4) + 1} team-card--minimal${
              member.name === "Yuvraj Verma" ? " team-card--featured" : ""
            }`}
          >
            <div className="team-card__media team-card__media--minimal">
              <img src={member.photo} alt={member.name} />
              <span className="team-role-badge">{member.role}</span>
            </div>
            <div className="team-card__body">
              <h3>{member.name}</h3>
              <div className="team-branch">{member.branch}</div>
              {member.summary ? <p className="team-card__summary">{member.summary}</p> : null}
              <div className="link-row">
                <a className="link-chip" href={member.linkedin} target="_blank" rel="noreferrer">
                  LinkedIn
                </a>
                <a className="link-chip" href={member.email}>
                  Email
                </a>
              </div>
              {member.name === "Yuvraj Verma" ? (
                <div className="team-card__actions">
                  {member.github ? (
                    <a
                      className="button-secondary team-action-button"
                      href={member.github}
                      target="_blank"
                      rel="noreferrer"
                    >
                      GitHub
                    </a>
                  ) : null}
                  {member.website ? (
                    <a
                      className="button-primary team-action-button"
                      href={member.website}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Website
                    </a>
                  ) : null}
                </div>
              ) : null}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
