import { NextRequest, NextResponse } from "next/server";

const ROOT_DOMAIN = "ai-grader.dev";
const DOCS_DOMAIN = `docs.${ROOT_DOMAIN}`;

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

  if (isAssetRequest(pathname)) {
    return NextResponse.next();
  }

  if (host === DOCS_DOMAIN && pathname === "/") {
    const url = request.nextUrl.clone();
    url.pathname = "/documentation";
    return NextResponse.rewrite(url);
  }

  if ((host === ROOT_DOMAIN || host === `www.${ROOT_DOMAIN}`) && pathname === "/documentation") {
    const docsUrl = new URL(`https://${DOCS_DOMAIN}/`);
    docsUrl.search = search;
    return NextResponse.redirect(docsUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/:path*"],
};
