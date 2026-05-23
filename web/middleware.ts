import { auth } from "@/lib/auth";

export default auth((req) => {
  const isAuthed = !!req.auth;
  const { pathname } = req.nextUrl;

  if (isAuthed) return;
  if (pathname.startsWith("/api/auth")) return;
  if (pathname.startsWith("/signin")) return;
  if (pathname.startsWith("/_next")) return;
  if (pathname === "/favicon.ico" || pathname === "/grant-engine-logo.svg") return;

  const url = req.nextUrl.clone();
  url.pathname = "/signin";
  url.searchParams.set("callbackUrl", pathname);
  return Response.redirect(url);
});

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
