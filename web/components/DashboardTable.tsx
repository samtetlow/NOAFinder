"use client";

import { useMemo, useState } from "react";

import { Filters, FilterState } from "./Filters";
import { formatMoney } from "@/lib/format";
import type { ClientRecord, Report } from "@/lib/types";

export function DashboardTable({ report }: { report: Report }) {
  const [filters, setFilters] = useState<FilterState>({
    query: "",
    agency: "",
    minAmount: "",
  });
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const agencies = useMemo(() => {
    const set = new Set<string>();
    for (const c of report.clients) {
      for (const a of c.awards) {
        if (a.awarding_agency) set.add(a.awarding_agency);
      }
    }
    return Array.from(set).sort();
  }, [report]);

  const filtered = useMemo(() => {
    const q = filters.query.trim().toLowerCase();
    const min = filters.minAmount ? Number(filters.minAmount) : 0;
    const agency = filters.agency;
    return report.clients
      .map((client) => {
        const awards = client.awards.filter((a) => {
          if (agency && a.awarding_agency !== agency) return false;
          if (min && (a.total_amount ?? 0) < min) return false;
          return true;
        });
        return { ...client, awards };
      })
      .filter((c) => {
        if (agency || min) {
          if (c.awards.length === 0) return false;
        }
        if (!q) return true;
        return (
          (c.task_title || "").toLowerCase().includes(q) ||
          c.uei.toLowerCase().includes(q)
        );
      });
  }, [report, filters]);

  function toggle(id: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  return (
    <div className="mt-2">
      <Filters
        filters={filters}
        setFilters={setFilters}
        agencies={agencies}
      />
      <div className="mt-4 overflow-hidden rounded-lg bg-white shadow-sm border border-brand/10">
        <table className="min-w-full text-sm">
          <thead className="bg-brand/5 text-brand-ink uppercase text-xs tracking-wide">
            <tr>
              <th className="text-left px-4 py-3 w-8"></th>
              <th className="text-left px-4 py-3">Client</th>
              <th className="text-left px-4 py-3">UEI</th>
              <th className="text-right px-4 py-3">Awards</th>
              <th className="text-right px-4 py-3">Total awarded</th>
              <th className="text-right px-4 py-3">Outlays</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-brand/60">
                  No clients match the current filters.
                </td>
              </tr>
            ) : null}
            {filtered.map((client) => (
              <ClientRow
                key={client.task_id}
                client={client}
                isOpen={expanded.has(client.task_id)}
                onToggle={() => toggle(client.task_id)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ClientRow({
  client, isOpen, onToggle,
}: {
  client: ClientRecord;
  isOpen: boolean;
  onToggle: () => void;
}) {
  return (
    <>
      <tr
        className="border-t border-brand/10 hover:bg-brand-mist cursor-pointer"
        onClick={onToggle}
      >
        <td className="px-4 py-3 text-brand/50">{isOpen ? "▾" : "▸"}</td>
        <td className="px-4 py-3 font-medium text-brand-ink">
          {client.task_title ?? client.task_id}
        </td>
        <td className="px-4 py-3 text-brand/70 font-mono text-xs">
          {client.uei}
        </td>
        <td className="px-4 py-3 text-right tabular-nums">
          {client.award_count.toLocaleString()}
        </td>
        <td className="px-4 py-3 text-right tabular-nums">
          {formatMoney(client.total_amount)}
        </td>
        <td className="px-4 py-3 text-right tabular-nums text-brand/70">
          {formatMoney(client.total_outlays)}
        </td>
      </tr>
      {isOpen ? (
        <tr className="bg-brand-mist/40 border-t border-brand/10">
          <td></td>
          <td colSpan={5} className="px-4 py-3">
            <div className="mb-2 text-xs uppercase tracking-wide text-brand/60">
              Awards · {" "}
              <a
                href={client.wrike_url}
                target="_blank" rel="noreferrer"
                className="underline hover:text-brand"
              >
                Open in Wrike →
              </a>
            </div>
            <AwardsTable awards={client.awards} />
          </td>
        </tr>
      ) : null}
    </>
  );
}

function AwardsTable({ awards }: { awards: ClientRecord["awards"] }) {
  if (awards.length === 0) {
    return (
      <div className="text-sm text-brand/60 italic">
        No awards match the current filters.
      </div>
    );
  }
  return (
    <div className="overflow-x-auto rounded border border-brand/10 bg-white">
      <table className="min-w-full text-sm">
        <thead className="bg-brand/5 text-brand-ink text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left px-3 py-2">Award ID</th>
            <th className="text-right px-3 py-2">Total</th>
            <th className="text-right px-3 py-2">Outlays</th>
            <th className="text-left px-3 py-2">Agency</th>
            <th className="text-left px-3 py-2">Type</th>
          </tr>
        </thead>
        <tbody>
          {awards.map((a, i) => (
            <tr key={(a.award_id ?? "") + i} className="border-t border-brand/10">
              <td className="px-3 py-2 font-mono text-xs">
                {a.url ? (
                  <a
                    href={a.url}
                    target="_blank" rel="noreferrer"
                    className="underline hover:text-brand"
                  >
                    {a.award_id ?? "(no id)"}
                  </a>
                ) : (
                  a.award_id ?? "(no id)"
                )}
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {formatMoney(a.total_amount)}
              </td>
              <td className="px-3 py-2 text-right tabular-nums text-brand/70">
                {formatMoney(a.outlay_amount)}
              </td>
              <td className="px-3 py-2">{a.awarding_agency ?? "—"}</td>
              <td className="px-3 py-2">{a.award_type ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
