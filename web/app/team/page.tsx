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

export default async function TeamPage() {
  const team = await fetchJson<TeamMember[]>("/api/team", fallbackTeam);

  return (
    <section className="team-minimal-page">
      <header className="team-minimal-header">
        <p className="team-minimal-header__eyebrow">Project Team</p>
        <h1>People Behind The System</h1>
        <p>
          A simple view of the members working on the grading platform and its academic product
          presentation.
        </p>
      </header>

      <div className="team-grid team-grid--minimal">
        {team.map((member, index) => (
          <article key={member.name} className={`team-card team-card--accent-${(index % 4) + 1} team-card--minimal`}>
            <img src={member.photo} alt={member.name} />
            <div className="team-card__body">
              <h3>{member.name}</h3>
              <div className="team-role">{member.role}</div>
              <div className="team-branch">{member.branch}</div>
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
    </section>
  );
}
