export interface AwardRecord {
  award_id: string | null;
  recipient: string | null;
  total_amount: number | null;
  outlay_amount: number | null;
  awarding_agency: string | null;
  award_type: string | null;
  url: string | null;
}

export interface ClientRecord {
  task_id: string;
  task_title: string | null;
  uei: string;
  wrike_url: string;
  award_count: number;
  total_amount: number;
  total_outlays: number;
  awards: AwardRecord[];
}

export interface ReportTotals {
  clients: number;
  awards: number;
  amount: number;
  outlays: number;
}

export interface Report {
  schema_version: number;
  generated_at: string;
  space_id: string;
  totals: ReportTotals;
  clients: ClientRecord[];
}
