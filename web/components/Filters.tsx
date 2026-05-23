"use client";

import type { Dispatch, SetStateAction } from "react";

export interface FilterState {
  query: string;
  agency: string;
  minAmount: string;
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
        placeholder="Search client name or UEI..."
        value={filters.query}
        onChange={(e) =>
          setFilters((s) => ({ ...s, query: e.target.value }))
        }
        className="flex-1 min-w-[200px] rounded border border-brand/20 px-3 py-2 text-sm bg-white focus:outline-none focus:border-brand"
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
    </div>
  );
}
