import { formatMoney } from "@/lib/format";
import type { ReportTotals } from "@/lib/types";

export function StatsBar({ totals }: { totals: ReportTotals }) {
  const cells = [
    { label: "Clients", value: totals.clients.toLocaleString() },
    { label: "Awards", value: totals.awards.toLocaleString() },
    { label: "Total awarded", value: formatMoney(totals.amount) },
    { label: "Total outlays", value: formatMoney(totals.outlays) },
  ];
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
      {cells.map((c) => (
        <div
          key={c.label}
          className="rounded-lg bg-white shadow-sm border border-brand/10 px-4 py-3"
        >
          <div className="text-xs uppercase tracking-wide text-brand/60">
            {c.label}
          </div>
          <div className="text-2xl font-semibold text-brand-ink tabular-nums">
            {c.value}
          </div>
        </div>
      ))}
    </div>
  );
}
