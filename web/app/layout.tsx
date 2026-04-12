import "./globals.css";
import type { Metadata } from "next";
import { SiteHeader } from "../components/site-header";
import { Analytics } from "@vercel/analytics/next";

export const metadata: Metadata = {
  title: "Automated Subjective Grader",
  description: "Web interface for the multimodal subjective answer sheet evaluation platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <SiteHeader />
          <main className="page-shell">{children}</main>
        </div>
        <Analytics />
      </body>
    </html>
  );
}
