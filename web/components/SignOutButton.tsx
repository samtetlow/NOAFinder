"use client";

import { signOut } from "next-auth/react";

export function SignOutButton() {
  return (
    <button
      type="button"
      onClick={() => signOut({ callbackUrl: "/" })}
      className="rounded border border-white/30 px-3 py-1 text-xs font-medium hover:bg-white/10"
    >
      Sign out
    </button>
  );
}
