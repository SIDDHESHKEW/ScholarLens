import React from 'react';
import type { RecommendationItem } from '../../types/api';
import { Modal } from '../common/Modal';
import { Badge } from '../common/Badge';
import { MatchFactorList } from './MatchFactorList';
import { formatScore, formatDimensionName } from '../../services/adapter';
import {
  ExternalLink,
  AlertTriangle,
  Building,
  Calendar,
  Award,
} from 'lucide-react';

interface ScholarshipDetailsModalProps {
  item: RecommendationItem | null;
  onClose: () => void;
}

export const ScholarshipDetailsModal: React.FC<ScholarshipDetailsModalProps> = ({
  item,
  onClose,
}) => {
  if (!item) return null;

  return (
    <Modal isOpen={!!item} onClose={onClose} title={item.title} maxWidth="max-w-3xl">
      <div className="space-y-6 text-slate-800 dark:text-slate-200">
        {/* Header Badges */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/70">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Rank #{item.rank}
            </span>
            <Badge status={item.eligibility.outcome} size="md" />
            <Badge status={item.verification.status} size="md" />
          </div>

          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span className="text-base font-extrabold text-slate-900 dark:text-slate-100">
              {formatScore(item.score)}
            </span>
          </div>
        </div>

        {/* Metadata: Provider, Deadline */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          {item.provider && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <Building className="w-4 h-4 text-slate-400 dark:text-slate-500" />
              <div>
                <span className="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold">
                  Awarding Organization
                </span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{item.provider}</span>
              </div>
            </div>
          )}

          {item.deadline && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <Calendar className="w-4 h-4 text-slate-400 dark:text-slate-500" />
              <div>
                <span className="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold">
                  Application Deadline
                </span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{item.deadline}</span>
              </div>
            </div>
          )}
        </div>

        {/* Unresolved Fields Notice (if POSSIBLY_ELIGIBLE) */}
        {item.eligibility.unknown_fields && item.eligibility.unknown_fields.length > 0 && (
          <div className="p-3.5 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-900 dark:text-amber-300 space-y-1">
            <div className="flex items-center gap-1.5 font-bold">
              <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
              <span>Unresolved Eligibility Information:</span>
            </div>
            <p className="text-amber-800 dark:text-amber-300/90 leading-relaxed">
              The following fields could not be verified from the scholarship database record:{' '}
              <strong className="underline">{item.eligibility.unknown_fields.join(', ')}</strong>.
              Review the official criteria to confirm final eligibility.
            </p>
          </div>
        )}

        {/* Score Breakdown Table */}
        {item.score_breakdown && item.score_breakdown.length > 0 && (
          <div className="space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Explainable Scoring Breakdown
            </h4>
            <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th className="py-2.5 px-3">Dimension</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Weight</th>
                    <th className="py-2.5 px-3">Points Earned</th>
                    <th className="py-2.5 px-3">Explanation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {item.score_breakdown.map((b) => (
                    <tr key={b.dimension} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
                      <td className="py-2.5 px-3 font-semibold text-slate-800 dark:text-slate-200">
                        {formatDimensionName(b.dimension)}
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge status={b.status} size="sm" />
                      </td>
                      <td className="py-2.5 px-3 text-slate-500 dark:text-slate-400">{b.weight} pts</td>
                      <td className="py-2.5 px-3 font-bold text-slate-900 dark:text-slate-100">
                        {b.contribution !== null ? `${b.contribution.toFixed(1)} pts` : '—'}
                      </td>
                      <td className="py-2.5 px-3 text-slate-600 dark:text-slate-400 max-w-xs">{b.explanation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Full Matching Factors */}
        <div className="space-y-2.5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Dimension Factors & Evidence
          </h4>
          <MatchFactorList factors={item.matching_factors} />
        </div>

        {/* Reasons */}
        {item.reasons && item.reasons.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Recommendation Factors
            </h4>
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300">
              <ul className="list-disc list-inside space-y-1">
                {item.reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Data & Verification Transparency */}
        <div className="space-y-2.5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Data & Verification
          </h4>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/70 space-y-3 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <span className="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold mb-1">
                  Status
                </span>
                <Badge status={item.verification.status} size="sm" />
              </div>
              <div>
                <span className="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold mb-1">
                  Freshness
                </span>
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {item.verification.freshness || 'UNKNOWN'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold mb-1">
                  Last Checked
                </span>
                <span className="text-slate-600 dark:text-slate-400">
                  {item.verification.verified_at
                    ? new Date(item.verification.verified_at).toLocaleDateString(undefined, {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })
                    : 'Not yet verified'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold mb-1">
                  Source
                </span>
                {item.official_source_url ? (
                  <span className="text-slate-700 dark:text-slate-300 truncate block">
                    {item.official_source_url}
                  </span>
                ) : (
                  <span className="text-slate-500 dark:text-slate-400">Imported dataset record</span>
                )}
              </div>
            </div>

            {item.verification.notes && (
              <div className="pt-2.5 border-t border-slate-200/80 dark:border-slate-700/60">
                <span className="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold mb-0.5">
                  Why
                </span>
                <p className="text-slate-600 dark:text-slate-300">{item.verification.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Warnings */}
        {item.warnings && item.warnings.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
              Verification & Data Notes
            </h4>
            <div className="p-3.5 rounded-xl bg-amber-50/70 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-900 dark:text-amber-300 space-y-1">
              {item.warnings.map((w, i) => (
                <div key={i} className="flex items-start gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  <span>{w}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Real Action Links */}
        <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-slate-500 dark:text-slate-400">
            Scholarship ID: <span className="font-mono text-slate-700 dark:text-slate-300">#{item.scholarship_id}</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {item.application_url ? (
              <a
                href={item.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-xl shadow-sm transition-colors"
              >
                <span>Visit Official Application Portal</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            ) : item.official_source_url ? (
              <a
                href={item.official_source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-bold text-white bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600 rounded-xl shadow-sm transition-colors"
              >
                <span>View Source Record Page</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            ) : (
              <span className="text-xs text-slate-400 dark:text-slate-500 italic">
                Official application link not provided by source dataset
              </span>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};
