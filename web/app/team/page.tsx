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

function mergeTeamMembers(fetched: TeamMember[], fallback: TeamMember[]): TeamMember[] {
  const fetchedByName = new Map(fetched.map((member) => [member.name, member]));
  const merged = fallback.map((member) => ({
    ...member,
    ...(fetchedByName.get(member.name) ?? {}),
  }));
  const knownNames = new Set(merged.map((member) => member.name));
  const additionalMembers = fetched.filter((member) => !knownNames.has(member.name));
  return [...merged, ...additionalMembers];
}

function SocialIcon({
  kind,
}: {
  kind: "linkedin" | "email" | "github" | "website";
}) {
  if (kind === "linkedin") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          fill="currentColor"
          d="M6.94 8.5H3.56V20h3.38V8.5ZM5.25 3A2.02 2.02 0 1 0 5.3 7.03 2.02 2.02 0 0 0 5.25 3Zm6.06 5.5H8.06V20h3.25v-6.03c0-1.59.3-3.14 2.27-3.14 1.94 0 1.97 1.82 1.97 3.25V20h3.25v-6.6c0-3.23-.7-5.72-4.47-5.72-1.81 0-3.02 1-3.52 1.95h-.05V8.5Z"
        />
      </svg>
    );
  }

  if (kind === "email") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          fill="currentColor"
          d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v11a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 17.5v-11Zm1.7.38 6.3 4.65 6.3-4.65A1 1 0 0 0 17.5 6h-11a1 1 0 0 0-.8.88Zm12.8 1.88-5.91 4.36a1 1 0 0 1-1.18 0L5.5 8.76v8.74c0 .55.45 1 1 1h11c.55 0 1-.45 1-1V8.76Z"
        />
      </svg>
    );
  }

  if (kind === "github") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          fill="currentColor"
          d="M12 .5a12 12 0 0 0-3.8 23.38c.6.1.82-.26.82-.58v-2.03c-3.34.73-4.04-1.41-4.04-1.41-.55-1.38-1.33-1.74-1.33-1.74-1.08-.74.08-.72.08-.72 1.2.08 1.83 1.21 1.83 1.21 1.05 1.8 2.77 1.28 3.45.98.11-.75.42-1.28.75-1.58-2.66-.3-5.46-1.31-5.46-5.84 0-1.29.47-2.35 1.22-3.18-.12-.3-.53-1.53.12-3.18 0 0 1-.32 3.3 1.21a11.7 11.7 0 0 1 6 0c2.3-1.53 3.3-1.21 3.3-1.21.65 1.65.24 2.88.12 3.18.76.83 1.22 1.89 1.22 3.18 0 4.54-2.8 5.53-5.47 5.83.43.37.81 1.08.81 2.18v3.23c0 .32.22.69.83.58A12 12 0 0 0 12 .5Z"
        />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12 3.5A8.5 8.5 0 0 0 6.03 18.03l-2.56 2.55a1 1 0 1 0 1.42 1.42l2.55-2.56A8.5 8.5 0 1 0 12 3.5Zm0 2A6.5 6.5 0 1 1 5.5 12 6.5 6.5 0 0 1 12 5.5Zm-1 2.5a1 1 0 0 0 0 2h2.59l-4.3 4.3a1 1 0 1 0 1.42 1.4l4.29-4.29V16a1 1 0 1 0 2 0V9a1 1 0 0 0-1-1h-7Z"
      />
    </svg>
  );
}

export default async function TeamPage() {
  const fetchedTeam = await fetchJson<TeamMember[]>("/api/team", fallbackTeam);
  const team = mergeTeamMembers(fetchedTeam, fallbackTeam);
  const featuredMember = team.find((member) => member.name === "Yuvraj Verma");

  return (
    <section className="team-minimal-page">
      <header className="team-minimal-header">
        <div className="team-minimal-header__copy">
          <p className="team-minimal-header__eyebrow">Project Team</p>
          <h1>People Behind The System</h1>
          <p>
            Meet the mentor and builders shaping the grading platform, from research direction to
            AI workflow design and product delivery.
          </p>
        </div>
        {featuredMember ? (
          <aside className="team-feature-panel">
            <span className="team-feature-panel__eyebrow">Featured Builder</span>
            <div className="team-feature-panel__main">
              <img src={featuredMember.photo} alt={featuredMember.name} />
              <div className="team-feature-panel__content">
                <h2>{featuredMember.name}</h2>
                <p className="team-feature-panel__meta">
                  {featuredMember.role} · {featuredMember.branch}
                </p>
                {featuredMember.summary ? <p>{featuredMember.summary}</p> : null}
              </div>
            </div>
            <div className="team-card__actions team-card__actions--feature">
              <a
                className="link-chip link-chip--icon"
                href={featuredMember.linkedin}
                target="_blank"
                rel="noreferrer"
              >
                <SocialIcon kind="linkedin" />
                LinkedIn
              </a>
              <a className="link-chip link-chip--icon" href={featuredMember.email}>
                <SocialIcon kind="email" />
                Email
              </a>
              {featuredMember.github ? (
                <a
                  className="button-secondary team-action-button"
                  href={featuredMember.github}
                  target="_blank"
                  rel="noreferrer"
                >
                  <SocialIcon kind="github" />
                  GitHub
                </a>
              ) : null}
              {featuredMember.website ? (
                <a
                  className="button-primary team-action-button"
                  href={featuredMember.website}
                  target="_blank"
                  rel="noreferrer"
                >
                  <SocialIcon kind="website" />
                  Website
                </a>
              ) : null}
            </div>
          </aside>
        ) : (
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
              <strong>Yuvraj Verma</strong>
            </article>
          </div>
        )}
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
              <div className="team-card__identity">
                <h3>{member.name}</h3>
                <div className="team-branch">{member.branch}</div>
              </div>
              {member.summary ? <p className="team-card__summary">{member.summary}</p> : null}
              <div className="link-row">
                <a
                  className="link-chip link-chip--icon"
                  href={member.linkedin}
                  target="_blank"
                  rel="noreferrer"
                >
                  <SocialIcon kind="linkedin" />
                  LinkedIn
                </a>
                <a className="link-chip link-chip--icon" href={member.email}>
                  <SocialIcon kind="email" />
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
                      <SocialIcon kind="github" />
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
                      <SocialIcon kind="website" />
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
