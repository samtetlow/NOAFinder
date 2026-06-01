import type { DashboardRow } from "./types";

// Two header rows — first names the two grouped sections (spanning 7 then
// 5 cells), second names each individual column. Mirrors the on-screen
// thead structure so the CSV reads the same way when opened in Excel.
const SECTION_HEADERS = [
  "USASpending.gov",
  "",
  "",
  "",
  "",
  "",
  "",
  "Grant Engine - Falcon",
  "",
  "",
  "",
  "",
];

const COLUMN_HEADERS = [
  // USASpending.gov
  "UEI",
  "Company Name",
  "Award Title / Description",
  "Prime Award ID",
  "Obligations $",
  "Outlay $",
  "Start Date",
  // Grant Engine - Falcon
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

function emptyDash(value: unknown): string {
  if (value === null || value === undefined) return "—";
  const s = String(value);
  return s === "" ? "—" : s;
}

function moneyCell(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  // Match the on-screen formatMoney(value, precise=false): no decimals,
  // thousands separators, leading "$".
  return "$" + Math.round(value).toLocaleString("en-US");
}

export function rowsToCsv(rows: DashboardRow[]): string {
  const lines = [
    SECTION_HEADERS.map(escape).join(","),
    COLUMN_HEADERS.map(escape).join(","),
  ];
  for (const r of rows) {
    lines.push(
      [
        emptyDash(r.uei),
        emptyDash(r.task_title),
        emptyDash(r.award_title),
        emptyDash(r.award_id),
        moneyCell(r.total_amount),
        moneyCell(r.outlay_amount),
        emptyDash(r.start_date),
        emptyDash(r.program_manager),
        emptyDash(r.uei),
        emptyDash(r.task_title),
        emptyDash(r.grant_number),
        emptyDash(r.project_title),
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
