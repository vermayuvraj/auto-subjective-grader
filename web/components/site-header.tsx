"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/evaluate", label: "Evaluate" },
  { href: "/documentation", label: "Documentation" },
  { href: "/team", label: "Team" },
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link href="/" className="brand-mark">
          <span className="brand-mark__icon">AG</span>
          <span>
            <strong>Auto Subjective Grader</strong>
            <small>Multimodal Evaluation Workspace</small>
          </span>
        </Link>
        <nav className="site-nav">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`site-nav__link${pathname === item.href ? " is-active" : ""}`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <Link href="/evaluate" className="button-primary site-header__cta">
          Run Evaluation
        </Link>
      </div>
    </header>
  );
}
