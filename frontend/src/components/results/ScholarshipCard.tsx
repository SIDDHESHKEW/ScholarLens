import React from 'react';
import type { RecommendationItem } from '../../types/api';
import { Badge } from '../common/Badge';
import { MatchFactorList } from './MatchFactorList';
import { formatScore } from '../../services/adapter';
import { AlertTriangle, ArrowUpRight, ExternalLink, Calendar, Building, Sparkles } from 'lucide-react';

interface ScholarshipCardProps {
  item: RecommendationItem;
  onSelect: (item: RecommendationItem) => void;
}

export const ScholarshipCard: React.FC<ScholarshipCardProps> = ({ item, onSelect }) => {
  const isScoreAvailable = item.score !== null && item.score !== undefined;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 shadow-sm hover:shadow-md transition-all p-6 flex flex-col justify-between gap-5">
      <div className="space-y-4">
        {/* Top Header Row: Rank, Badges & Score */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3.5">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-md bg-slate-900 dark:bg-slate-700 text-white flex items-center justify-center font-bold text-xs font-mono">
              #{item.rank}
            </span>
            <Badge status={item.eligibility.outcome} size="sm" />
            {item.verification.status && (
              <Badge status={item.verification.status} size="sm" />
            )}
          </div>

          <div className="text-right">
            {isScoreAvailable ? (
              <div className="flex flex-col items-end">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-blue-50 dark:bg-blue-950/80 border border-blue-200 dark:border-blue-800 text-blue-900 dark:text-blue-300">
                  <Sparkles className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                  <span className="text-xs font-bold">{formatScore(item.score)}</span>
                </div>
                {item.score === 0 && (
                  <span className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">
                    No matching factors
                  </span>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-end">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded border border-slate-200 dark:border-slate-700">
                  Score unavailable
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Title & Provider */}
        <div className="space-y-2">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 leading-snug line-clamp-2">
              {item.title}
            </h3>
            <div className="flex flex-wrap items-center gap-4 mt-1.5 text-xs text-slate-500 dark:text-slate-400">
              {item.provider && (
                <span className="flex items-center gap-1">
                  <Building className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
                  <span>{item.provider}</span>
                </span>
              )}
              {item.deadline && (
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
                  <span>Deadline: {item.deadline}</span>
                </span>
              )}
            </div>
          </div>

          {/* Primary External Action at TOP */}
          <div className="pt-1">
            {item.application_url ? (
              <a
                href={item.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 shadow-sm shadow-blue-600/20 transition-all focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
                title="Visit Official Application Portal"
              >
                <span>Visit Official Application Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            ) : item.official_source_url ? (
              <a
                href={item.official_source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-slate-600"
                title="View Official Source"
              >
                <span>View Official Source</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            ) : (
              <span className="text-[11px] text-slate-400 dark:text-slate-500 italic block">
                Official application link not provided.
              </span>
            )}
          </div>
        </div>

        {/* Compact matching factors */}
        <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80">
          <span className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">
            Factor Compatibility
          </span>
          <MatchFactorList factors={item.matching_factors} compact />
        </div>

        {/* Reasons preview */}
        {item.reasons && item.reasons.length > 0 && (
          <div className="p-3 rounded-xl bg-slate-50/80 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60 text-xs text-slate-700 dark:text-slate-300 space-y-1">
            <span className="font-bold text-slate-900 dark:text-slate-100 block text-[11px] uppercase tracking-wider">
              Why this matched:
            </span>
            <ul className="list-disc list-inside space-y-0.5 text-slate-600 dark:text-slate-400 text-[11px]">
              {item.reasons.slice(0, 2).map((r, i) => (
                <li key={i} className="line-clamp-1">
                  {r}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Data & Verification Section */}
        <div className="p-3 rounded-xl bg-slate-50/90 dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700/80 space-y-1.5 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 dark:text-slate-500">
              Data & Verification
            </span>
            <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">
              {item.verification.status || 'UNVERIFIED'}
            </span>
          </div>

          {item.warnings && item.warnings.length > 0 ? (
            <div className="space-y-1 pt-1">
              {item.warnings.map((w, idx) => (
                <div key={idx} className="flex items-start gap-1.5 text-[11px] text-amber-800 dark:text-amber-300/90">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  <span className="line-clamp-2">{w}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-700 dark:text-emerald-400">
              <Sparkles className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span>Verified from available source</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer action (Secondary) */}
      <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <button
          type="button"
          onClick={() => onSelect(item)}
          className="w-full inline-flex items-center justify-center gap-1.5 py-2.5 px-4 text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 bg-slate-50/80 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 rounded-xl transition-colors"
        >
          <span>View Full Evaluation Details</span>
          <ArrowUpRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
