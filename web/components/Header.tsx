import Image from "next/image";

import { SignOutButton } from "./SignOutButton";

export function Header({ userEmail }: { userEmail?: string | null }) {
  return (
    <header className="bg-brand text-white">
      <div className="mx-auto max-w-7xl px-6 py-5 flex items-center gap-4">
        <Image
          src="/grant-engine-logo.svg"
          alt="Grant Engine"
          width={44}
          height={44}
          priority
          className="rounded"
        />
        <div className="flex-1">
          <div className="text-xl font-semibold tracking-tight">NOA Finder</div>
          <div className="text-xs text-white/70">by Grant Engine</div>
        </div>
        {userEmail ? (
          <div className="flex items-center gap-3 text-sm">
            <span className="text-white/80 hidden sm:block">{userEmail}</span>
            <SignOutButton />
          </div>
        ) : null}
      </div>
    </header>
  );
}
