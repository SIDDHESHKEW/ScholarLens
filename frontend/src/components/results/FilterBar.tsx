import React from 'react';
import type { FilterState, FilterEligibility, SortOrder } from '../../types/ui';

interface FilterBarProps {
  filter: FilterState;
  onFilterChange: (newFilter: FilterState) => void;
  totalCount: number;
  filteredCount: number;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filter,
  onFilterChange,
  totalCount,
  filteredCount,
}) => {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm mb-6 transition-colors">
      {/* Eligibility Tab Pills */}
      <div className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg">
        {(['ALL', 'ELIGIBLE', 'POSSIBLY_ELIGIBLE'] as FilterEligibility[]).map((tab) => {
          const isActive = filter.eligibility === tab;
          const label =
            tab === 'ALL'
              ? 'All Matches'
              : tab === 'ELIGIBLE'
              ? 'Eligible Only'
              : 'Possibly Eligible';

          return (
            <button
              key={tab}
              onClick={() => onFilterChange({ ...filter, eligibility: tab })}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                isActive
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              {label}
            </button>
          );
        })}
      </div>

      {/* Sorting dropdown & Counter */}
      <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
        <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
          Showing <strong className="text-slate-700 dark:text-slate-200">{filteredCount}</strong> of <strong className="text-slate-700 dark:text-slate-200">{totalCount}</strong>
        </span>

        <div className="flex items-center gap-2">
          <label htmlFor="sort-select" className="text-xs text-slate-500 dark:text-slate-400 font-medium">
            Sort by:
          </label>
          <select
            id="sort-select"
            value={filter.sort}
            onChange={(e) => onFilterChange({ ...filter, sort: e.target.value as SortOrder })}
            className="text-xs font-semibold px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="DEFAULT">Recommended Rank (Default)</option>
            <option value="SCORE_DESC">Score (Highest First)</option>
            <option value="TITLE_ASC">Title (A-Z)</option>
          </select>
        </div>
      </div>
    </div>
  );
};
