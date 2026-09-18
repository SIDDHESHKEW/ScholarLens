import React from 'react';
import type { MatchFactor } from '../../types/api';
import { Badge } from '../common/Badge';
import { formatDimensionName } from '../../services/adapter';

interface MatchFactorListProps {
  factors: MatchFactor[];
  compact?: boolean;
}

export const MatchFactorList: React.FC<MatchFactorListProps> = ({ factors, compact = false }) => {
  if (compact) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
        {factors.map((f) => (
          <div
            key={f.dimension}
            className="p-2.5 rounded-xl bg-slate-50/80 dark:bg-slate-800/70 border border-slate-100 dark:border-slate-700/60 flex flex-col justify-between gap-1.5 transition-colors"
          >
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 dark:text-slate-500 truncate">
              {formatDimensionName(f.dimension)}
            </span>
            <div>
              <Badge status={f.status} size="sm" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      {factors.map((f) => (
        <div
          key={f.dimension}
          className="p-3 rounded-xl bg-slate-50/80 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 dark:text-slate-100">
                {formatDimensionName(f.dimension)}
              </span>
              <Badge status={f.status} size="sm" />
            </div>
            <p className="text-slate-600 dark:text-slate-300 text-xs">{f.explanation}</p>
          </div>

          {(f.student_value !== undefined || f.scholarship_value !== undefined) && (
            <div className="text-[11px] text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-200/80 dark:border-slate-700 shrink-0">
              <div>
                <strong className="text-slate-600 dark:text-slate-300">Student:</strong>{' '}
                <span className="text-slate-800 dark:text-slate-200">{String(f.student_value ?? 'Not set')}</span>
              </div>
              <div>
                <strong className="text-slate-600 dark:text-slate-300">Requirement:</strong>{' '}
                <span className="text-slate-800 dark:text-slate-200">{String(f.scholarship_value ?? 'Unrestricted')}</span>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
