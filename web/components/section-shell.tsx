import { ReactNode } from "react";

type SectionShellProps = {
  title: string;
  subtitle: string;
  children: ReactNode;
};

export function SectionShell({ title, subtitle, children }: SectionShellProps) {
  return (
    <section className="section-shell">
      <div className="section-shell__header">
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
      {children}
    </section>
  );
}
