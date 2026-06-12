import { APPS } from "@/lib/apps";
import { AppTileGrid, mainAppsToTiles } from "@/components/AppTileGrid";

export const dynamic = "force-dynamic";

export default function LaunchpadHome() {
  return (
    <div className="p-8 max-w-6xl">
      <header className="mb-8">
        <div className="text-xs uppercase tracking-wide text-brand/50">
          Grant Engine
        </div>
        <h1 className="text-3xl font-semibold text-brand-ink mt-1">
          Launchpad
        </h1>
        <p className="text-sm text-brand/60 mt-2 max-w-2xl">
          One sign-on for every Grant Engine tool. Pick an application below
          or navigate directly from the left sidebar.
        </p>
      </header>
      <AppTileGrid tiles={mainAppsToTiles(APPS)} />
    </div>
  );
}
