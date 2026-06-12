import { DashboardTable } from "@/components/DashboardTable";
import { loadReport } from "@/lib/data";
import { formatDate } from "@/lib/format";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "NOA Finder · Grant Engine",
};

export default async function NoaFinderPage() {
  const report = await loadReport();
  return (
    <div className="p-8">
      <header className="mb-6 flex items-baseline justify-between gap-4 flex-wrap">
        <div>
          <div className="text-xs uppercase tracking-wide text-brand/50">
            Delivery
          </div>
          <h1 className="text-2xl font-semibold text-brand-ink mt-1">
            NOA Finder
          </h1>
          <p className="text-sm text-brand/60 mt-1">
            Cross-referenced from Falcon client UEIs against USASpending.gov.
          </p>
        </div>
        <div className="text-xs text-brand/60 leading-tight text-right">
          <div className="uppercase tracking-wide text-[10px] text-brand/50">
            Snapshot generated
          </div>
          <div>{formatDate(report.generated_at)}</div>
        </div>
      </header>
      <DashboardTable report={report} />
    </div>
  );
}
