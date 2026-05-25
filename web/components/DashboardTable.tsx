"use client";

import { useMemo, useState } from "react";

import { Filters, FilterState } from "./Filters";
import { downloadCsv, rowsToCsv, todayStamp } from "@/lib/csv";
import { formatMoney } from "@/lib/format";
import type { DashboardRow, Report, SortKey } from "@/lib/types";

function flattenReport(report: Report): DashboardRow[] {
  const rows: DashboardRow[] = [];
  for (const c of report.clients) {
    if (c.awards.length === 0) {
      rows.push({
        task_id: c.task_id,
        task_title: c.task_title,
        uei: c.uei,
        wrike_url: c.wrike_url,
        program_manager: c.program_manager,
        grant_number: c.grant_number,
        project_title: c.project_title,
        award_id: null,
        award_title: null,
        award_type: null,
        awarding_agency: null,
        total_amount: null,
        outlay_amount: null,
        start_date: null,
        award_url: null,
      });
      continue;
    }
    for (const a of c.awards) {
      rows.push({
        task_id: c.task_id,
        task_title: c.task_title,
        uei: c.uei,
        wrike_url: c.wrike_url,
        program_manager: c.program_manager,
        grant_number: c.grant_number,
        project_title: c.project_title,
        award_id: a.award_id,
        award_title: a.description || a.recipient,
        award_type: a.award_type,
        awarding_agency: a.awarding_agency,
        total_amount: a.total_amount,
        outlay_amount: a.outlay_amount,
        start_date: a.start_date,
        award_url: a.url,
      });
    }
  }
  return rows;
}

function sortRows(rows: DashboardRow[], key: SortKey): DashboardRow[] {
  const sorted = [...rows];
  if (key === "customer") {
    sorted.sort((a, b) =>
      (a.task_title || "").localeCompare(b.task_title || ""),
    );
  } else if (key === "current_pm") {
    sorted.sort((a, b) => {
      // Nulls last
      const av = a.program_manager || "￿";
      const bv = b.program_manager || "￿";
      const cmp = av.localeCompare(bv);
      if (cmp !== 0) return cmp;
      return (a.task_title || "").localeCompare(b.task_title || "");
    });
  } else {
    sorted.sort(
      (a, b) => (b.total_amount ?? 0) - (a.total_amount ?? 0),
    );
  }
  return sorted;
}

export function DashboardTable({ report }: { report: Report }) {
  const [filters, setFilters] = useState<FilterState>({
    query: "",
    agency: "",
    minAmount: "",
    sort: "amount_desc",
  });

  const allRows = useMemo(() => flattenReport(report), [report]);

  const agencies = useMemo(() => {
    const set = new Set<string>();
    for (const r of allRows) {
      if (r.awarding_agency) set.add(r.awarding_agency);
    }
    return Array.from(set).sort();
  }, [allRows]);

  const filteredRows = useMemo(() => {
    const q = filters.query.trim().toLowerCase();
    const min = filters.minAmount ? Number(filters.minAmount) : 0;
    const agency = filters.agency;
    const filtered = allRows.filter((r) => {
      if (agency && r.awarding_agency !== agency) return false;
      if (min && (r.total_amount ?? 0) < min) return false;
      if (q) {
        const hay = [
          r.task_title,
          r.uei,
          r.award_id,
          r.award_title,
          r.program_manager,
          r.grant_number,
          r.project_title,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    return sortRows(filtered, filters.sort);
  }, [allRows, filters]);

  function handleExport() {
    const csv = rowsToCsv(filteredRows);
    downloadCsv(csv, `noa-finder-${todayStamp()}.csv`);
  }

  return (
    <div className="mt-2">
      <div className="flex items-end gap-3 mt-6 flex-wrap">
        <div className="flex-1 min-w-[260px]">
          <Filters
            filters={filters}
            setFilters={setFilters}
            agencies={agencies}
          />
        </div>
        <button
          type="button"
          onClick={handleExport}
          disabled={filteredRows.length === 0}
          className="rounded border border-brand/30 bg-white px-4 py-2 text-sm font-medium text-brand hover:bg-brand hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition"
          title="Export the rows currently visible to CSV"
        >
          Export CSV
        </button>
      </div>

      <div className="mt-4 text-xs text-brand/60">
        {filteredRows.length} row{filteredRows.length === 1 ? "" : "s"}
      </div>

      <div className="mt-2 overflow-x-auto rounded-lg bg-white shadow-sm border border-brand/10">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-brand text-white text-xs uppercase tracking-wide">
              <th
                colSpan={7}
                className="text-left px-4 py-2 border-r border-white/20"
              >
                USASpending.gov
              </th>
              <th colSpan={5} className="text-left px-4 py-2">
                Grant Engine – Falcon
              </th>
            </tr>
            <tr className="bg-brand/5 text-brand-ink uppercase text-[11px] tracking-wide">
              <th className="text-left px-3 py-2 font-semibold">UEI</th>
              <th className="text-left px-3 py-2 font-semibold">Company Name</th>
              <th className="text-left px-3 py-2 font-semibold">
                Award Title / Description
              </th>
              <th className="text-left px-3 py-2 font-semibold">
                Prime Award ID
              </th>
              <th className="text-right px-3 py-2 font-semibold">
                Obligations $
              </th>
              <th className="text-right px-3 py-2 font-semibold">Outlay $</th>
              <th className="text-left px-3 py-2 font-semibold border-r border-brand/15">
                Start Date
              </th>
              <th className="text-left px-3 py-2 font-semibold">
                Current PM
              </th>
              <th className="text-left px-3 py-2 font-semibold">UEI</th>
              <th className="text-left px-3 py-2 font-semibold">
                Company Name
              </th>
              <th className="text-left px-3 py-2 font-semibold">
                Grant Number
              </th>
              <th className="text-left px-3 py-2 font-semibold">
                Project Title
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredRows.length === 0 ? (
              <tr>
                <td
                  colSpan={12}
                  className="px-4 py-8 text-center text-brand/60"
                >
                  No rows match the current filters.
                </td>
              </tr>
            ) : null}
            {filteredRows.map((r, i) => (
              <tr
                key={`${r.task_id}-${r.award_id ?? "no-award"}-${i}`}
                className="border-t border-brand/10 hover:bg-brand-mist/50"
              >
                <td className="px-3 py-2 font-mono text-xs">{r.uei}</td>
                <td className="px-3 py-2 font-medium text-brand-ink">
                  <a
                    href={r.wrike_url}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:underline"
                  >
                    {r.task_title ?? r.task_id}
                  </a>
                </td>
                <td className="px-3 py-2 max-w-[280px] truncate" title={r.award_title ?? undefined}>
                  {r.award_title ?? "—"}
                </td>
                <td className="px-3 py-2 font-mono text-xs">
                  {r.award_url ? (
                    <a
                      href={r.award_url}
                      target="_blank"
                      rel="noreferrer"
                      className="underline hover:text-brand"
                    >
                      {r.award_id ?? "—"}
                    </a>
                  ) : (
                    r.award_id ?? "—"
                  )}
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {formatMoney(r.total_amount)}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-brand/70">
                  {formatMoney(r.outlay_amount)}
                </td>
                <td className="px-3 py-2 text-brand/70 border-r border-brand/15">
                  {r.start_date ?? "—"}
                </td>
                <td className="px-3 py-2">{r.program_manager ?? "—"}</td>
                <td className="px-3 py-2 font-mono text-xs">{r.uei}</td>
                <td className="px-3 py-2 font-medium text-brand-ink">
                  {r.task_title ?? "—"}
                </td>
                <td className="px-3 py-2 font-mono text-xs">
                  {r.grant_number ?? "—"}
                </td>
                <td className="px-3 py-2">{r.project_title ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
