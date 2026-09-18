import React, { useState, useMemo } from 'react';
import type { RecommendationResponse, RecommendationItem } from '../types/api';
import type { FilterState } from '../types/ui';
import { SummaryPanel } from '../components/results/SummaryPanel';
import { FilterBar } from '../components/results/FilterBar';
import { ScholarshipCard } from '../components/results/ScholarshipCard';
import { ScholarshipDetailsModal } from '../components/results/ScholarshipDetailsModal';
import { EmptyState } from '../components/results/EmptyState';
import { ArrowLeft, RefreshCw } from 'lucide-react';

interface ResultsPageProps {
  response: RecommendationResponse;
  onEditProfile: () => void;
  onRefresh: () => void;
}

export const ResultsPage: React.FC<ResultsPageProps> = ({
  response,
  onEditProfile,
  onRefresh,
}) => {
  const [filter, setFilter] = useState<FilterState>({
    eligibility: 'ALL',
    sort: 'DEFAULT',
    minScore: 0,
  });

  const [selectedScholarship, setSelectedScholarship] = useState<RecommendationItem | null>(null);

  // Presentation-only filtering & sorting (Backend ranking remains authoritative)
  const filteredRecommendations = useMemo(() => {
    let list = [...response.recommendations];

    // Filter by eligibility status
    if (filter.eligibility === 'ELIGIBLE') {
      list = list.filter((r) => r.eligibility.outcome === 'ELIGIBLE');
    } else if (filter.eligibility === 'POSSIBLY_ELIGIBLE') {
      list = list.filter((r) => r.eligibility.outcome === 'POSSIBLY_ELIGIBLE');
    }

    // Sort options
    if (filter.sort === 'SCORE_DESC') {
      list.sort((a, b) => (b.score ?? -1) - (a.score ?? -1));
    } else if (filter.sort === 'TITLE_ASC') {
      list.sort((a, b) => a.title.localeCompare(b.title));
    }

    return list;
  }, [response.recommendations, filter]);

  return (
    <div className="py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      {/* Top action navigation & Header */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <button
            type="button"
            onClick={onEditProfile}
            className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Adjust Profile & Preferences</span>
          </button>

          <button
            type="button"
            onClick={onRefresh}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 shadow-xs transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Re-run Prediction</span>
          </button>
        </div>

        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Your Recommendation Results
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Personalized scholarship evaluations ranked by deterministic eligibility and factor compatibility.
          </p>
        </div>
      </div>

      {/* Summary Dashboard */}
      <SummaryPanel response={response} />

      {/* Filter and Sort controls */}
      <FilterBar
        filter={filter}
        onFilterChange={setFilter}
        totalCount={response.recommendations.length}
        filteredCount={filteredRecommendations.length}
      />

      {/* Results Grid or Empty Filter State */}
      {filteredRecommendations.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          {filteredRecommendations.map((item) => (
            <ScholarshipCard
              key={item.scholarship_id}
              item={item}
              onSelect={setSelectedScholarship}
            />
          ))}
        </div>
      ) : (
        <EmptyState type="filtered_out" onEditProfile={onEditProfile} />
      )}

      {/* Modal for detailed breakdown */}
      <ScholarshipDetailsModal
        item={selectedScholarship}
        onClose={() => setSelectedScholarship(null)}
      />
    </div>
  );
};
