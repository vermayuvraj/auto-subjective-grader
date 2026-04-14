import type { MetadataRoute } from "next";
import { DOCUMENTATION_HREF } from "../lib/documentation";
import { SITE_URL, absoluteUrl } from "../lib/seo";

function resolveDocumentationUrl(): string {
  return DOCUMENTATION_HREF.startsWith("http")
    ? DOCUMENTATION_HREF
    : absoluteUrl(DOCUMENTATION_HREF);
}

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();

  return [
    {
      url: SITE_URL,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: absoluteUrl("/evaluate"),
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.9,
    },
    {
      url: resolveDocumentationUrl(),
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: absoluteUrl("/team"),
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.6,
    },
  ];
}

