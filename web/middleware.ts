import { NextRequest, NextResponse } from "next/server";

const REPORT_PATH = "/documentation.html";
const LEGACY_REPORT_PATH = "/project-report.html";
const configuredDocumentationUrl =
  process.env.DOCUMENTATION_URL?.trim() || process.env.NEXT_PUBLIC_DOCUMENTATION_URL?.trim() || "";

function getDocumentationHost() {
  if (!configuredDocumentationUrl) {
    return "";
  }

  try {
    return new URL(configuredDocumentationUrl).host.toLowerCase();
  } catch {
    return "";
  }
}

function getRootDomainFromDocsHost(docsHost: string) {
  return docsHost.startsWith("docs.") ? docsHost.slice(5) : "";
}

function isAssetRequest(pathname: string) {
  return (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname === "/favicon.ico" ||
    /\.[^/]+$/.test(pathname)
  );
}

export function middleware(request: NextRequest) {
  const host = request.headers.get("host")?.split(":")[0].toLowerCase() ?? "";
  const { pathname, search } = request.nextUrl;
  const docsHost = getDocumentationHost();
  const rootDomain = getRootDomainFromDocsHost(docsHost);

  if (pathname === LEGACY_REPORT_PATH) {
    const url = request.nextUrl.clone();
    url.pathname = REPORT_PATH;
    return NextResponse.redirect(url);
  }

  if (isAssetRequest(pathname)) {
    return NextResponse.next();
  }

  if (docsHost && host === docsHost && (pathname === "/" || pathname === "/documentation")) {
    const url = request.nextUrl.clone();
    url.pathname = REPORT_PATH;
    return NextResponse.rewrite(url);
  }

  if (
    rootDomain &&
    (host === rootDomain || host === `www.${rootDomain}`) &&
    (pathname === "/documentation" || pathname === REPORT_PATH || pathname === LEGACY_REPORT_PATH)
  ) {
    const docsUrl = new URL(configuredDocumentationUrl);
    docsUrl.pathname = "/";
    docsUrl.search = search;
    return NextResponse.redirect(docsUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/:path*"],
};
