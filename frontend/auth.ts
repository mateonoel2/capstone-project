import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";

declare module "next-auth" {
  interface Session {
    githubAccessToken?: string;
    user: {
      id?: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }
}

declare module "@auth/core/jwt" {
  interface JWT {
    githubAccessToken?: string;
  }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GitHub],
  callbacks: {
    jwt({ token, account }) {
      if (account?.access_token) {
        token.githubAccessToken = account.access_token;
      }
      return token;
    },
    session({ session, token }) {
      session.githubAccessToken = token.githubAccessToken;
      return session;
    },
  },
  pages: {
    signIn: "/login",
  },
});
