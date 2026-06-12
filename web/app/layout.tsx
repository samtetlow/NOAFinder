import type { Metadata } from "next";
import { Lato } from "next/font/google";
import { SessionProvider } from "next-auth/react";

import "./globals.css";

const lato = Lato({
  weight: ["400", "700", "900"],
  subsets: ["latin"],
  variable: "--font-lato",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Launchpad · Grant Engine",
  description:
    "Grant Engine application hub: marketing, capture, product funding, and delivery tools under one sign-on.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={lato.variable}>
      <body className="font-sans">
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
