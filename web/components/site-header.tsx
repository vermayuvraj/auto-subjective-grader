"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { SVGProps, useEffect, useState } from "react";
import { DOCUMENTATION_HREF } from "../lib/documentation";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/evaluate", label: "Evaluate" },
  { href: DOCUMENTATION_HREF, label: "Documentation", openInNewTab: true },
  { href: "/team", label: "Team" },
];

function ThemeIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M12 3v2.5" />
      <path d="M12 18.5V21" />
      <path d="m5.64 5.64 1.77 1.77" />
      <path d="m16.59 16.59 1.77 1.77" />
      <path d="M3 12h2.5" />
      <path d="M18.5 12H21" />
      <path d="m5.64 18.36 1.77-1.77" />
      <path d="m16.59 7.41 1.77-1.77" />
      <circle cx="12" cy="12" r="4" />
    </svg>
  );
}

export function SiteHeader() {
  const pathname = usePathname();
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const savedTheme = window.localStorage.getItem("ai-grader-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const darkMode = savedTheme ? savedTheme === "dark" : prefersDark;
    document.documentElement.dataset.theme = darkMode ? "dark" : "light";
    setIsDarkMode(darkMode);
  }, []);

  function toggleTheme() {
    const nextIsDark = !isDarkMode;
    document.documentElement.dataset.theme = nextIsDark ? "dark" : "light";
    window.localStorage.setItem("ai-grader-theme", nextIsDark ? "dark" : "light");
    setIsDarkMode(nextIsDark);
  }

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
              target={item.openInNewTab ? "_blank" : undefined}
              rel={item.openInNewTab ? "noreferrer" : undefined}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="site-header__actions">
          <button type="button" className="theme-toggle" onClick={toggleTheme}>
            <ThemeIcon width={16} height={16} />
            {isDarkMode ? "Light" : "Dark"}
          </button>
          <Link href="/evaluate" className="button-primary site-header__cta site-header__cta--compact">
            Run Evaluation
          </Link>
        </div>
      </div>
    </header>
  );
}
