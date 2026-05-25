import { auth } from "@/lib/auth";
import { DashboardTable } from "@/components/DashboardTable";
import { Header } from "@/components/Header";
import { loadReport } from "@/lib/data";

export const dynamic = "force-dynamic";

export default async function Page() {
  const session = await auth();
  const report = await loadReport();

  return (
    <>
      <Header
        userEmail={session?.user?.email}
        snapshotAt={report.generated_at}
      />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <div>
          <h1 className="text-2xl font-semibold text-brand-ink">
            Federal awards by client
          </h1>
          <p className="text-sm text-brand/60 mt-1">
            Cross-referenced from Falcon client UEIs against USASpending.gov.
          </p>
        </div>
        <DashboardTable report={report} />
      </main>
    </>
  );
}
