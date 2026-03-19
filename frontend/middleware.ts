import { auth } from "@/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  if (!req.auth) {
    const loginUrl = new URL("/login", req.url);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
});

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - /login
     * - /api/auth/* (NextAuth routes)
     * - _next/static, _next/image, favicon.ico, public assets
     */
    "/((?!login|api/auth|_next/static|_next/image|favicon\\.ico).*)",
  ],
};
