import Link from "next/link";

import type { MainApp, SubApp } from "@/lib/apps";

interface AppTile {
  title: string;
  description?: string;
  href: string;
  comingSoon?: boolean;
}

export function AppTileGrid({
  tiles,
  cols = 2,
}: {
  tiles: AppTile[];
  cols?: 2 | 3;
}) {
  const gridCls =
    cols === 3
      ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
      : "grid grid-cols-1 sm:grid-cols-2 gap-4";
  return (
    <div className={gridCls}>
      {tiles.map((t) => (
        <Link
          key={t.href}
          href={t.href}
          className="block rounded-xl bg-white border border-brand/10 p-5 hover:border-brand/40 hover:shadow-md transition"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="text-lg font-semibold text-brand-ink">
              {t.title}
            </div>
            {t.comingSoon ? (
              <span className="text-[10px] uppercase tracking-wide bg-brand/5 text-brand px-2 py-0.5 rounded">
                Soon
              </span>
            ) : null}
          </div>
          {t.description ? (
            <p className="text-sm text-brand/60 mt-2">{t.description}</p>
          ) : null}
        </Link>
      ))}
    </div>
  );
}

export function mainAppsToTiles(apps: MainApp[]): AppTile[] {
  return apps.map((a) => ({
    title: a.title,
    description: a.description,
    href: a.href,
    comingSoon: a.comingSoon,
  }));
}

export function subAppsToTiles(subs: SubApp[]): AppTile[] {
  return subs.map((s) => ({
    title: s.title,
    description: s.description,
    href: s.href,
    comingSoon: s.comingSoon,
  }));
}
