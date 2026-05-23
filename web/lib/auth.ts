import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

const allowedDomain = process.env.ALLOWED_GOOGLE_DOMAIN || "";

export const { handlers, auth, signIn, signOut } = NextAuth({
  trustHost: true,
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
  ],
  callbacks: {
    async signIn({ profile }) {
      if (!allowedDomain) return true;
      const email = profile?.email ?? "";
      const domain = email.split("@")[1]?.toLowerCase();
      return domain === allowedDomain.toLowerCase();
    },
  },
  pages: {
    signIn: "/signin",
  },
});
