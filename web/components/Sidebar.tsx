"use client";

import Image from "next/image";
import Link from "next/link";
import { signOut } from "next-auth/react";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { APPS, type MainApp } from "@/lib/apps";

interface SidebarProps {
  userEmail?: string | null;
}

export function Sidebar({ userEmail }: SidebarProps) {
  const pathname = usePathname();

  // Auto-expand any group whose sub-tree contains the current path.
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    for (const app of APPS) {
      if (app.subs && pathname.startsWith(app.href)) init[app.slug] = true;
    }
    return init;
  });

  function toggleGroup(slug: string) {
    setOpenGroups((prev) => ({ ...prev, [slug]: !prev[slug] }));
  }

  return (
    <aside className="w-64 shrink-0 bg-brand text-white min-h-screen flex flex-col">
      <Link
        href="/"
        className="px-5 py-5 flex items-center gap-3 border-b border-white/10 hover:bg-white/5 transition"
      >
        <Image
          src="/grant-engine-logo.svg"
          alt="Grant Engine"
          width={32}
          height={32}
          priority
          className="brightness-0 invert"
        />
        <div className="leading-tight">
          <div className="font-semibold tracking-tight">Launchpad</div>
          <div className="text-xs text-white/60">Grant Engine</div>
        </div>
      </Link>

      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        <SidebarLink href="/" label="Home" active={pathname === "/"} />
        <div className="my-2 border-t border-white/10" />
        {APPS.map((app) => (
          <AppNavGroup
            key={app.slug}
            app={app}
            pathname={pathname}
            isOpen={Boolean(openGroups[app.slug])}
            onToggle={() => toggleGroup(app.slug)}
          />
        ))}
      </nav>

      {userEmail ? (
        <div className="border-t border-white/10 px-4 py-4">
          <div
            className="text-xs text-white/70 truncate mb-2"
            title={userEmail}
          >
            {userEmail}
          </div>
          <button
            type="button"
            onClick={() => signOut({ callbackUrl: "/" })}
            className="text-xs rounded border border-white/30 px-3 py-1 hover:bg-white/10 transition"
          >
            Sign out
          </button>
        </div>
      ) : null}
    </aside>
  );
}

function SidebarLink({
  href,
  label,
  active,
}: {
  href: string;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={
        "block px-3 py-2 rounded text-sm font-medium transition " +
        (active
          ? "bg-white/15 text-white"
          : "text-white/80 hover:bg-white/5 hover:text-white")
      }
    >
      {label}
    </Link>
  );
}

function AppNavGroup({
  app,
  pathname,
  isOpen,
  onToggle,
}: {
  app: MainApp;
  pathname: string;
  isOpen: boolean;
  onToggle: () => void;
}) {
  const isActive =
    pathname === app.href || pathname.startsWith(app.href + "/");

  if (!app.subs) {
    return <SidebarLink href={app.href} label={app.title} active={isActive} />;
  }

  return (
    <div>
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={isOpen}
        className={
          "w-full text-left px-3 py-2 rounded text-sm font-medium flex items-center justify-between transition " +
          (isActive
            ? "bg-white/15 text-white"
            : "text-white/80 hover:bg-white/5 hover:text-white")
        }
      >
        <span>{app.title}</span>
        <span
          className={
            "text-[10px] transition-transform " +
            (isOpen ? "rotate-90" : "")
          }
        >
          ▸
        </span>
      </button>
      {isOpen ? (
        <div className="ml-3 mt-0.5 mb-1 space-y-0.5 border-l border-white/10 pl-3">
          {app.subs.map((sub) => (
            <Link
              key={sub.slug}
              href={sub.href}
              className={
                "block px-3 py-1.5 rounded text-sm transition " +
                (pathname === sub.href
                  ? "bg-white/15 text-white"
                  : "text-white/70 hover:bg-white/5 hover:text-white")
              }
            >
              {sub.title}
              {sub.comingSoon ? (
                <span className="ml-2 text-[10px] uppercase tracking-wide text-white/40">
                  soon
                </span>
              ) : null}
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}
