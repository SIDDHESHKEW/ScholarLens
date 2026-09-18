import React from 'react';
import type { RecommendationResponse } from '../../types/api';
import { Award, ShieldAlert, Layers, CheckCircle2 } from 'lucide-react';

interface SummaryPanelProps {
  response: RecommendationResponse;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ response }) => {
  const { total_candidates, recommended_count, excluded, recommendations } = response;

  const eligibleCount = recommendations.filter((r) => r.eligibility.outcome === 'ELIGIBLE').length;
  const possiblyEligibleCount = recommendations.filter(
    (r) => r.eligibility.outcome === 'POSSIBLY_ELIGIBLE'
  ).length;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 mb-8 transition-colors">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-5 mb-5">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2.5 py-1 rounded-full border border-blue-200 dark:border-blue-800">
            Engine Evaluation Audit
          </span>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-2">
            Evaluation Summary & Audit
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Evaluated using Policy {response.recommendation_policy_version} • Scoring Policy {response.scoring_policy_version}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold border border-slate-200 dark:border-slate-700">
            Profile Status: {response.student_profile_status.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Candidates Evaluated */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-1">
          <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400 text-xs font-medium">
            <Layers className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Total Evaluated</span>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">{total_candidates}</div>
          <p className="text-[11px] text-slate-400 dark:text-slate-500">Total database candidates</p>
        </div>

        {/* Recommended Count */}
        <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/50 space-y-1">
          <div className="flex items-center gap-1.5 text-blue-700 dark:text-blue-300 text-xs font-medium">
            <Award className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Recommended</span>
          </div>
          <div className="text-2xl font-black text-blue-950 dark:text-blue-100">{recommended_count}</div>
          <p className="text-[11px] text-blue-600 dark:text-blue-400">
            {eligibleCount} Eligible • {possiblyEligibleCount} Possible
          </p>
        </div>

        {/* Quality Blocked */}
        <div className="p-4 rounded-xl bg-purple-50/40 dark:bg-purple-950/30 border border-purple-100 dark:border-purple-900/50 space-y-1">
          <div className="flex items-center gap-1.5 text-purple-700 dark:text-purple-300 text-xs font-medium">
            <CheckCircle2 className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            <span>Quality Blocked</span>
          </div>
          <div className="text-2xl font-black text-purple-950 dark:text-purple-100">{excluded.quality_blocked_count}</div>
          <p className="text-[11px] text-purple-600 dark:text-purple-400">Specific major mismatches filtered</p>
        </div>

        {/* Not Eligible */}
        <div className="p-4 rounded-xl bg-rose-50/40 dark:bg-rose-950/30 border border-rose-100 dark:border-rose-900/50 space-y-1">
          <div className="flex items-center gap-1.5 text-rose-700 dark:text-rose-300 text-xs font-medium">
            <ShieldAlert className="w-4 h-4 text-rose-600 dark:text-rose-400" />
            <span>Not Eligible</span>
          </div>
          <div className="text-2xl font-black text-rose-950 dark:text-rose-100">{excluded.not_eligible_count}</div>
          <p className="text-[11px] text-rose-600 dark:text-rose-400">Disqualified by hard eligibility</p>
        </div>
      </div>
    </div>
  );
};
