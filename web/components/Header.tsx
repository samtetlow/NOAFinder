import Image from "next/image";

import { SignOutButton } from "./SignOutButton";
import { formatDate } from "@/lib/format";

interface HeaderProps {
  userEmail?: string | null;
  snapshotAt?: string | null;
}

export function Header({ userEmail, snapshotAt }: HeaderProps) {
  return (
    <header className="bg-brand text-white">
      <div className="mx-auto max-w-7xl px-6 py-5 flex items-center gap-4">
        <Image
          src="/grant-engine-logo.svg"
          alt="Grant Engine"
          width={44}
          height={44}
          priority
          className="rounded brightness-0 invert"
        />
        <div className="flex-1">
          <div className="text-xl font-semibold tracking-tight">NOA Finder</div>
          <div className="text-xs text-white/70">by Grant Engine</div>
        </div>
        {snapshotAt ? (
          <div className="hidden md:block text-right text-xs text-white/70 leading-tight">
            <div className="uppercase tracking-wide text-[10px] text-white/50">
              Snapshot generated
            </div>
            <div className="text-white/90">{formatDate(snapshotAt)}</div>
          </div>
        ) : null}
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
