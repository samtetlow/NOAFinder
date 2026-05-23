"use client";

import Image from "next/image";
import { signIn } from "next-auth/react";

export default function SignInPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-brand-mist px-6">
      <div className="w-full max-w-md rounded-2xl bg-white shadow-md p-8 border border-brand/10">
        <div className="flex items-center gap-3 mb-6">
          <Image
            src="/grant-engine-logo.svg"
            alt="Grant Engine"
            width={48} height={48}
          />
          <div>
            <div className="text-lg font-semibold text-brand-ink">NOA Finder</div>
            <div className="text-xs text-brand/60">by Grant Engine</div>
          </div>
        </div>
        <h1 className="text-xl font-semibold text-brand-ink mb-2">Sign in</h1>
        <p className="text-sm text-brand/70 mb-6">
          Sign in with your Grant Engine Google account to view the awards
          dashboard.
        </p>
        <button
          type="button"
          onClick={() => signIn("google", { callbackUrl: "/" })}
          className="w-full rounded-lg bg-brand text-white py-3 font-medium hover:bg-brand-ink transition"
        >
          Continue with Google
        </button>
      </div>
    </main>
  );
}
