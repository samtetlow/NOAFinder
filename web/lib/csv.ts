import type { DashboardRow } from "./types";

const HEADERS = [
  // USASpending.gov
  "UEI",
  "Company Name",
  "Award Title / Description",
  "Prime Award ID",
  "Obligations $",
  "Outlay $",
  "Start Date",
  // Grant Engine – Falcon
  "Current Program Manager",
  "UEI",
  "Company Name",
  "Grant Number",
  "Project Title",
];

function escape(value: unknown): string {
  if (value === null || value === undefined) return "";
  const s = String(value);
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

export function rowsToCsv(rows: DashboardRow[]): string {
  const lines = [HEADERS.map(escape).join(",")];
  for (const r of rows) {
    lines.push(
      [
        r.uei,
        r.task_title,
        r.award_title,
        r.award_id,
        r.total_amount,
        r.outlay_amount,
        r.start_date,
        r.program_manager,
        r.uei,
        r.task_title,
        r.grant_number,
        r.project_title,
      ].map(escape).join(","),
    );
  }
  return lines.join("\n") + "\n";
}

export function downloadCsv(content: string, filename: string): void {
  const blob = new Blob([content], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function todayStamp(): string {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}
