import type { Metadata } from "next";
import { SessionProvider } from "next-auth/react";

import "./globals.css";

export const metadata: Metadata = {
  title: "NOA Finder · Grant Engine",
  description:
    "Cross-reference Grant Engine clients with USASpending.gov federal awards.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
