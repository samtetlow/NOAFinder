import Link from "next/link";

import type { MainApp, SubApp } from "@/lib/apps";

interface AppTile {
  title: string;
  description?: string;
  href: string;
  comingSoon?: boolean;
  external?: boolean;
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
        <Tile key={t.href} tile={t} />
      ))}
    </div>
  );
}

function Tile({ tile }: { tile: AppTile }) {
  const cardCls =
    "block rounded-xl bg-white border border-brand/10 p-5 hover:border-brand/40 hover:shadow-md transition";
  const inner = (
    <>
      <div className="flex items-start justify-between gap-3">
        <div className="text-lg font-semibold text-brand-ink">
          {tile.title}
          {tile.external ? (
            <span className="ml-1 text-xs text-brand/50" aria-hidden>
              ↗
            </span>
          ) : null}
        </div>
        {tile.comingSoon ? (
          <span className="text-[10px] uppercase tracking-wide bg-brand/5 text-brand px-2 py-0.5 rounded">
            Soon
          </span>
        ) : null}
      </div>
      {tile.description ? (
        <p className="text-sm text-brand/60 mt-2">{tile.description}</p>
      ) : null}
    </>
  );
  if (tile.external) {
    return (
      <a href={tile.href} target="_blank" rel="noreferrer" className={cardCls}>
        {inner}
      </a>
    );
  }
  return (
    <Link href={tile.href} className={cardCls}>
      {inner}
    </Link>
  );
}

export function mainAppsToTiles(apps: MainApp[]): AppTile[] {
  return apps.map((a) => ({
    title: a.title,
    description: a.description,
    href: a.href,
    comingSoon: a.comingSoon,
    external: a.external,
  }));
}

export function subAppsToTiles(subs: SubApp[]): AppTile[] {
  return subs.map((s) => ({
    title: s.title,
    description: s.description,
    href: s.href,
    comingSoon: s.comingSoon,
    external: s.external,
  }));
}
