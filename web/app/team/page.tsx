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
          d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
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
          d="M12 .5C5.373.5 0 5.873 0 12.5c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.508 11.508 0 0 1 12 6.303c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 22.297 24 17.8 24 12.5 24 5.873 18.627.5 12 .5z"
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
  const mentor =
    team.find((member) => member.role.toLowerCase().includes("mentor")) ?? team[0] ?? null;
  const members = mentor ? team.filter((member) => member.name !== mentor.name) : team;

  return (
    <section className="team-showcase-page">
      <header className="team-showcase-header">
        <p className="team-showcase-meta">Project Team</p>
        <h1>People Behind the System</h1>
        <p className="team-showcase-sub">
          The team building the Automated Subjective Answer Sheet Evaluation System at RECK.
        </p>
      </header>

      {mentor ? (
        <article className="mentor-row">
          <img className="avatar-lg" src={mentor.photo} alt={mentor.name} />
          <div className="mentor-text">
            <div className="mentor-tag">{mentor.role}</div>
            <div className="mentor-name">{mentor.name}</div>
            <div className="mentor-dept">{mentor.branch}</div>
          </div>
          <div className="mentor-links">
            <a className="team-button team-button--filled" href={mentor.linkedin} target="_blank" rel="noreferrer">
              <SocialIcon kind="linkedin" />
              LinkedIn
            </a>
            <a className="team-button" href={mentor.email}>
              <SocialIcon kind="email" />
              Email
            </a>
          </div>
        </article>
      ) : null}

      <div className="section-label">Student Members</div>

      <div className="member-list">
        {members.map((member, index) => (
          <article
            key={member.name}
            className={`member-row member-row--accent-${(index % 3) + 1}`}
          >
            <img className="avatar-md" src={member.photo} alt={member.name} />
            <div className="member-info">
              <div className="member-name">{member.name}</div>
              <div className="member-meta">
                <span className="role-dot" />
                <span>{member.role}</span>
                <span className="sep">·</span>
                <span>{member.branch}</span>
              </div>
            </div>
            <div className="member-actions">
              <a
                className="team-button team-button--filled"
                href={member.linkedin}
                target="_blank"
                rel="noreferrer"
              >
                <SocialIcon kind="linkedin" />
                LinkedIn
              </a>
              {member.github ? (
                <a className="team-button" href={member.github} target="_blank" rel="noreferrer">
                  <SocialIcon kind="github" />
                  GitHub
                </a>
              ) : null}
              {member.website ? (
                <a className="team-button" href={member.website} target="_blank" rel="noreferrer">
                  <SocialIcon kind="website" />
                  Website
                </a>
              ) : null}
              <a className="team-button" href={member.email}>
                <SocialIcon kind="email" />
                Email
              </a>
            </div>
          </article>
        ))}
      </div>

      <footer className="team-showcase-footer">
        <span>Built at RECK · Department of Electronics Engineering · Batch 2022-26</span>
        <span>Ai Grader · Automated Subjective Answer Sheet Evaluation System</span>
      </footer>
    </section>
  );
}
