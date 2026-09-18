import React from 'react';
import { SearchX, AlertCircle, RefreshCw, Edit3 } from 'lucide-react';

interface EmptyStateProps {
  type: 'no_results' | 'filtered_out' | 'error';
  errorMessage?: string;
  onEditProfile?: () => void;
  onRetry?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  type,
  errorMessage,
  onEditProfile,
  onRetry,
}) => {
  if (type === 'error') {
    return (
      <div className="p-8 sm:p-12 text-center bg-white dark:bg-slate-900 rounded-2xl border border-red-200 dark:border-red-900/60 shadow-sm max-w-xl mx-auto my-12 space-y-4">
        <div className="w-14 h-14 rounded-full bg-red-50 dark:bg-red-950/80 text-red-600 dark:text-red-400 flex items-center justify-center mx-auto border border-red-200 dark:border-red-800">
          <AlertCircle className="w-7 h-7" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          We couldn't complete the prediction right now
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
          {errorMessage ||
            'The recommendation engine encountered a communication issue. Please ensure the backend server is active.'}
        </p>
        {onRetry && (
          <div className="pt-2">
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-xl transition-colors shadow-sm"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry Prediction</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  if (type === 'filtered_out') {
    return (
      <div className="p-8 sm:p-12 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm max-w-xl mx-auto my-12 space-y-4">
        <div className="w-14 h-14 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 flex items-center justify-center mx-auto">
          <SearchX className="w-7 h-7" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          No matches match your current filter
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
          Try switching between "All Matches" and "Eligible Only" to inspect opportunities.
        </p>
      </div>
    );
  }

  return (
    <div className="p-8 sm:p-12 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm max-w-xl mx-auto my-12 space-y-4">
      <div className="w-14 h-14 rounded-full bg-blue-50 dark:bg-blue-950/80 text-blue-600 dark:text-blue-400 flex items-center justify-center mx-auto border border-blue-200 dark:border-blue-800">
        <SearchX className="w-7 h-7" />
      </div>
      <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">
        No scholarships matched your profile
      </h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
        ScholarMatch evaluated your academic criteria against all candidates, but hard eligibility restrictions or the Recommendation Quality Gate filtered out conflicting disciplines.
      </p>
      {onEditProfile && (
        <div className="pt-2">
          <button
            onClick={onEditProfile}
            className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-xl transition-colors shadow-sm"
          >
            <Edit3 className="w-4 h-4" />
            <span>Adjust Profile Parameters</span>
          </button>
        </div>
      )}
    </div>
  );
};
