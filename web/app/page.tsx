import { auth } from "@/lib/auth";
import { DashboardTable } from "@/components/DashboardTable";
import { Header } from "@/components/Header";
import { StatsBar } from "@/components/StatsBar";
import { loadReport } from "@/lib/data";
import { formatDate } from "@/lib/format";

export const dynamic = "force-dynamic";

export default async function Page() {
  const session = await auth();
  const report = await loadReport();

  return (
    <>
      <Header userEmail={session?.user?.email} />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex items-baseline justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-semibold text-brand-ink">
              Federal awards by client
            </h1>
            <p className="text-sm text-brand/60 mt-1">
              Cross-referenced from Wrike client UEIs against USASpending.gov.
            </p>
          </div>
          <div className="text-xs text-brand/60">
            Snapshot generated {formatDate(report.generated_at)}
          </div>
        </div>
        <StatsBar totals={report.totals} />
        <DashboardTable report={report} />
      </main>
    </>
  );
}
