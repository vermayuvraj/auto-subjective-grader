"use client";

import Image from "next/image";
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
          <Image
            src="/brand/ai-grader-logo.png"
            alt="Ai Grader"
            width={877}
            height={173}
            priority
            className="brand-mark__logo"
          />
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
