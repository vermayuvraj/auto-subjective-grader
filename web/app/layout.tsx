import "./globals.css";
import type { Metadata } from "next";
import { SiteHeader } from "../components/site-header";
import {
  GOOGLE_SITE_VERIFICATION,
  SITE_DESCRIPTION,
  SITE_KEYWORDS,
  SITE_NAME,
  SITE_OG_IMAGE,
  SITE_TITLE,
  SITE_URL,
  absoluteUrl,
} from "../lib/seo";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} | ${SITE_TITLE}`,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  keywords: SITE_KEYWORDS,
  authors: [
    {
      name: "Ai Grader Team",
      url: SITE_URL,
    },
  ],
  creator: "Ai Grader Team",
  publisher: "Ai Grader",
  category: "education",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    url: SITE_URL,
    siteName: SITE_NAME,
    title: `${SITE_NAME} | ${SITE_TITLE}`,
    description: SITE_DESCRIPTION,
    images: [
      {
        url: absoluteUrl(SITE_OG_IMAGE),
        width: 877,
        height: 173,
        alt: "Ai Grader logo",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE_NAME} | ${SITE_TITLE}`,
    description: SITE_DESCRIPTION,
    images: [absoluteUrl(SITE_OG_IMAGE)],
  },
  verification: GOOGLE_SITE_VERIFICATION
    ? {
        google: GOOGLE_SITE_VERIFICATION,
      }
    : undefined,
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },
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
      </body>
    </html>
  );
}
