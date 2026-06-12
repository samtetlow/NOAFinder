import { APPS } from "@/lib/apps";
import { AppTileGrid, subAppsToTiles } from "@/components/AppTileGrid";

export default function MarketingHub() {
  const app = APPS.find((a) => a.slug === "marketing")!;
  return (
    <div className="p-8 max-w-6xl">
      <header className="mb-8">
        <div className="text-xs uppercase tracking-wide text-brand/50">
          Application
        </div>
        <h1 className="text-3xl font-semibold text-brand-ink mt-1">
          {app.title}
        </h1>
        <p className="text-sm text-brand/60 mt-2 max-w-2xl">
          {app.description}
        </p>
      </header>
      <AppTileGrid tiles={subAppsToTiles(app.subs!)} cols={3} />
    </div>
  );
}
