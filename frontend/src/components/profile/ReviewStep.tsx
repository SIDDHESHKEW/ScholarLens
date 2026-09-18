import React from 'react';
import type { StudentProfileFormState } from '../../types/profile';
import {
  EDUCATION_LEVEL_OPTIONS,
  FIELD_OF_STUDY_OPTIONS,
  STUDY_MODE_OPTIONS,
  FUNDING_PREFERENCE_OPTIONS,
  COUNTRY_OPTIONS,
} from '../../types/profile';
import { CheckCircle2, ArrowRight, Edit3 } from 'lucide-react';

interface ReviewStepProps {
  form: StudentProfileFormState;
  onEdit: () => void;
  onSubmit: () => void;
  includePossiblyEligible: boolean;
  onToggleIncludePossiblyEligible: (val: boolean) => void;
  limit: number;
  onLimitChange: (val: number) => void;
  isSubmitting: boolean;
}

export const ReviewStep: React.FC<ReviewStepProps> = ({
  form,
  onEdit,
  onSubmit,
  includePossiblyEligible,
  onToggleIncludePossiblyEligible,
  limit,
  onLimitChange,
  isSubmitting,
}) => {
  const getLabel = (options: { value: string; label: string }[], value: string) => {
    return options.find((o) => o.value === value)?.label || value;
  };

  const fieldDisplay =
    form.field_of_study === 'other'
      ? form.custom_field_of_study || 'Other'
      : getLabel(FIELD_OF_STUDY_OPTIONS, form.field_of_study);

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-white">Review Your Profile</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Verify your parameters before running the evaluation. The backend will evaluate hard eligibility, contradiction evidence, and explainable ranking.
        </p>
      </div>

      {/* Structured Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Personal & Geographic */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 pb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
              Personal & Location
            </span>
          </div>
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Age:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">{form.age} years</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Nationality:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {getLabel(COUNTRY_OPTIONS, form.nationality)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Residence Country:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {getLabel(COUNTRY_OPTIONS, form.residence_country)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Gender / Targeting:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200 capitalize">{form.gender}</span>
            </div>
          </div>
        </div>

        {/* Education */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 pb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
              Academic Standing
            </span>
          </div>
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Education Level:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {getLabel(EDUCATION_LEVEL_OPTIONS, form.education_level)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Field of Study:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">{fieldDisplay}</span>
            </div>
            {form.degree && (
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Degree:</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{form.degree}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">GPA / Marks:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {form.gpa ? `${form.gpa} GPA` : 'Not specified'}{' '}
                {form.academic_percentage ? `(${form.academic_percentage}%)` : ''}
              </span>
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 pb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
              Study Preferences
            </span>
          </div>
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Preferred Destination:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {getLabel(COUNTRY_OPTIONS, form.preferred_study_country)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Study Mode:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {getLabel(STUDY_MODE_OPTIONS, form.study_mode)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Funding Preference:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {getLabel(FUNDING_PREFERENCE_OPTIONS, form.funding_preference)}
              </span>
            </div>
          </div>
        </div>

        {/* Additional */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 pb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
              Financial & Accessibility
            </span>
          </div>
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Annual Household Income:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {form.family_income
                  ? `${form.family_income} ${form.family_income_currency}`
                  : 'Not specified'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Disability Scheme Eligible:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {form.disability_status ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Advanced API Controls */}
      <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
          Recommendation Scope & Settings
        </h4>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={includePossiblyEligible}
              onChange={(e) => onToggleIncludePossiblyEligible(e.target.checked)}
              className="w-4 h-4 rounded text-blue-600 border-slate-300 dark:border-slate-700 focus:ring-blue-500 bg-white dark:bg-slate-800"
            />
            <span>
              Include <strong>Possibly Eligible</strong> scholarships (where requirements are unresolved)
            </span>
          </label>

          <div className="flex items-center gap-2 text-xs">
            <label htmlFor="limit-select" className="text-slate-500 dark:text-slate-400">
              Result Limit:
            </label>
            <select
              id="limit-select"
              value={limit}
              onChange={(e) => onLimitChange(parseInt(e.target.value, 10))}
              className="px-2 py-1 rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 font-semibold text-slate-800 dark:text-slate-200"
            >
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
            </select>
          </div>
        </div>
      </div>

      {/* Buttons */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
        <button
          type="button"
          onClick={onEdit}
          disabled={isSubmitting}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 text-sm font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 rounded-xl transition-colors"
        >
          <Edit3 className="w-4 h-4" />
          <span>Edit Profile</span>
        </button>

        <button
          type="button"
          onClick={onSubmit}
          disabled={isSubmitting}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 text-base font-bold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:bg-blue-400 rounded-xl shadow-lg shadow-blue-600/20 transition-all focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
        >
          <CheckCircle2 className="w-5 h-5" />
          <span>Predict My Scholarships</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
