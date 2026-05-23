import fs from "node:fs/promises";
import path from "node:path";

import type { Report } from "./types";

const REPORT_PATH = path.join(process.cwd(), "public", "data", "report.json");

export async function loadReport(): Promise<Report> {
  const raw = await fs.readFile(REPORT_PATH, "utf-8");
  return JSON.parse(raw) as Report;
}
