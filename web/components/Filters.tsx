"use client";

import type { Dispatch, SetStateAction } from "react";

import type { SortDir, SortKey } from "@/lib/types";

export interface FilterState {
  query: string;
  sortKey: SortKey;
  sortDir: SortDir;
}

interface Props {
  filters: FilterState;
  setFilters: Dispatch<SetStateAction<FilterState>>;
}

export function Filters({ filters, setFilters }: Props) {
  function handleSort(key: SortKey) {
    setFilters((s) => {
      if (s.sortKey === key) {
        return { ...s, sortDir: s.sortDir === "asc" ? "desc" : "asc" };
      }
      return { ...s, sortKey: key, sortDir: "asc" };
    });
  }

  return (
    <div className="flex flex-wrap gap-3 mt-6 items-center">
      <input
        type="search"
        placeholder="Search company, UEI, award ID, PM, or grant #..."
        value={filters.query}
        onChange={(e) =>
          setFilters((s) => ({ ...s, query: e.target.value }))
        }
        className="flex-1 min-w-[260px] rounded border border-brand/20 px-3 py-2 text-sm bg-white focus:outline-none focus:border-brand"
      />
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wide text-brand/60">
          Sort
        </span>
        <SortButton
          label="Customer Name"
          active={filters.sortKey === "customer"}
          dir={filters.sortDir}
          onClick={() => handleSort("customer")}
        />
        <SortButton
          label="Current PM"
          active={filters.sortKey === "current_pm"}
          dir={filters.sortDir}
          onClick={() => handleSort("current_pm")}
        />
      </div>
    </div>
  );
}

interface SortButtonProps {
  label: string;
  active: boolean;
  dir: SortDir;
  onClick: () => void;
}

function SortButton({ label, active, dir, onClick }: SortButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={
        "rounded px-3 py-1.5 text-sm font-medium border transition " +
        (active
          ? "bg-brand text-white border-brand"
          : "bg-white text-brand border-brand/20 hover:border-brand/40")
      }
    >
      {label}
      {active ? (
        <span className="ml-1 text-xs">{dir === "asc" ? "↓" : "↑"}</span>
      ) : null}
    </button>
  );
}
