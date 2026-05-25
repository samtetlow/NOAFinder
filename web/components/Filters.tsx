"use client";

import type { Dispatch, SetStateAction } from "react";

import type { SortKey } from "@/lib/types";

export interface FilterState {
  query: string;
  agency: string;
  minAmount: string;
  sort: SortKey;
}

interface Props {
  filters: FilterState;
  setFilters: Dispatch<SetStateAction<FilterState>>;
  agencies: string[];
}

export function Filters({ filters, setFilters, agencies }: Props) {
  return (
    <div className="flex flex-wrap gap-3 mt-6">
      <input
        type="search"
        placeholder="Search company, UEI, or award ID..."
        value={filters.query}
        onChange={(e) =>
          setFilters((s) => ({ ...s, query: e.target.value }))
        }
        className="flex-1 min-w-[220px] rounded border border-brand/20 px-3 py-2 text-sm bg-white focus:outline-none focus:border-brand"
      />
      <select
        value={filters.agency}
        onChange={(e) =>
          setFilters((s) => ({ ...s, agency: e.target.value }))
        }
        className="rounded border border-brand/20 px-3 py-2 text-sm bg-white focus:outline-none focus:border-brand"
      >
        <option value="">All agencies</option>
        {agencies.map((a) => (
          <option key={a} value={a}>{a}</option>
        ))}
      </select>
      <input
        type="number"
        inputMode="numeric"
        placeholder="Min $ awarded"
        value={filters.minAmount}
        onChange={(e) =>
          setFilters((s) => ({ ...s, minAmount: e.target.value }))
        }
        className="w-40 rounded border border-brand/20 px-3 py-2 text-sm bg-white focus:outline-none focus:border-brand"
      />
      <select
        value={filters.sort}
        onChange={(e) =>
          setFilters((s) => ({ ...s, sort: e.target.value as SortKey }))
        }
        className="rounded border border-brand/20 px-3 py-2 text-sm bg-white focus:outline-none focus:border-brand"
        aria-label="Sort by"
      >
        <option value="amount_desc">Sort: Total awarded ↓</option>
        <option value="customer">Sort: Customer (A–Z)</option>
        <option value="current_pm">Sort: Current PM (A–Z)</option>
      </select>
    </div>
  );
}
