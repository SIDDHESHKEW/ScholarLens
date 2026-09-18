import React from 'react';
import type { MatchStatus } from '../../types/api';
import { CheckCircle2, AlertCircle, HelpCircle, XCircle } from 'lucide-react';

interface BadgeProps {
  status: 'ELIGIBLE' | 'POSSIBLY_ELIGIBLE' | 'NOT_ELIGIBLE' | MatchStatus | string;
  size?: 'sm' | 'md';
  showIcon?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({ status, size = 'sm', showIcon = true }) => {
  const normalized = status.toUpperCase();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700';
  let label = status;
  let Icon = HelpCircle;

  switch (normalized) {
    case 'ELIGIBLE':
      colorClasses =
        'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950/70 dark:text-emerald-300 dark:border-emerald-800';
      label = 'Eligible';
      Icon = CheckCircle2;
      break;
    case 'POSSIBLY_ELIGIBLE':
      colorClasses =
        'bg-amber-50 text-amber-800 border-amber-300 dark:bg-amber-950/70 dark:text-amber-300 dark:border-amber-800';
      label = 'Possibly Eligible';
      Icon = AlertCircle;
      break;
    case 'NOT_ELIGIBLE':
      colorClasses =
        'bg-rose-50 text-rose-800 border-rose-300 dark:bg-rose-950/70 dark:text-rose-300 dark:border-rose-800';
      label = 'Not Eligible';
      Icon = XCircle;
      break;
    case 'MATCH':
      colorClasses =
        'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-850';
      label = 'Match';
      Icon = CheckCircle2;
      break;
    case 'PARTIAL_MATCH':
      colorClasses =
        'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-850';
      label = 'Partial';
      Icon = AlertCircle;
      break;
    case 'MISMATCH':
      colorClasses =
        'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-850';
      label = 'Mismatch';
      Icon = XCircle;
      break;
    case 'UNKNOWN':
      colorClasses =
        'bg-slate-50 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700';
      label = 'Unknown';
      Icon = HelpCircle;
      break;
    case 'VERIFIED':
      colorClasses =
        'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950/70 dark:text-emerald-300 dark:border-emerald-800';
      label = 'Verified';
      Icon = CheckCircle2;
      break;
    case 'PARTIALLY_VERIFIED':
      colorClasses =
        'bg-sky-50 text-sky-800 border-sky-300 dark:bg-sky-950/70 dark:text-sky-300 dark:border-sky-800';
      label = 'Partially Verified';
      Icon = CheckCircle2;
      break;
    case 'UNVERIFIED':
      colorClasses =
        'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700';
      label = 'Unverified';
      Icon = HelpCircle;
      break;
    case 'NEEDS_REVIEW':
      colorClasses =
        'bg-amber-50 text-amber-800 border-amber-300 dark:bg-amber-950/70 dark:text-amber-300 dark:border-amber-800';
      label = 'Needs Review';
      Icon = AlertCircle;
      break;
    case 'SOURCE_UNAVAILABLE':
      colorClasses =
        'bg-orange-50 text-orange-800 border-orange-300 dark:bg-orange-950/70 dark:text-orange-300 dark:border-orange-800';
      label = 'Source Unavailable';
      Icon = AlertCircle;
      break;
    case 'STALE':
      colorClasses =
        'bg-purple-50 text-purple-800 border-purple-300 dark:bg-purple-950/70 dark:text-purple-300 dark:border-purple-800';
      label = 'Stale';
      Icon = AlertCircle;
      break;
    case 'CONTRADICTED':
      colorClasses =
        'bg-rose-50 text-rose-800 border-rose-300 dark:bg-rose-950/70 dark:text-rose-300 dark:border-rose-800';
      label = 'Contradicted';
      Icon = XCircle;
      break;
    default:
      label = status;
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center gap-1 font-medium rounded-md border ${sizeClasses} ${colorClasses}`}
    >
      {showIcon && <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />}
      <span>{label}</span>
    </span>
  );
};
