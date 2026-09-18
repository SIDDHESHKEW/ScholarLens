import React from 'react';
import type { StudentProfileFormState } from '../../types/profile';
import {
  COUNTRY_OPTIONS,
  STUDY_MODE_OPTIONS,
  FUNDING_PREFERENCE_OPTIONS,
  INSTITUTION_TYPE_OPTIONS,
} from '../../types/profile';

interface PreferencesStepProps {
  form: StudentProfileFormState;
  onChange: (field: keyof StudentProfileFormState, value: unknown) => void;
}

export const PreferencesStep: React.FC<PreferencesStepProps> = ({ form, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-white">Study Preferences</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Specify where and how you wish to study. In Phase 7 scoring, Study Country carries 20% weight, Study Mode carries 10%, and Funding carries 15%.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Preferred Study Country */}
        <div>
          <label htmlFor="pref-country-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Preferred Destination Country <span className="text-red-500">*</span>
          </label>
          <select
            id="pref-country-select"
            value={form.preferred_study_country}
            onChange={(e) => onChange('preferred_study_country', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {COUNTRY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Canonical aliases (e.g. USA, US) are automatically resolved.</p>
        </div>

        {/* Study Mode */}
        <div>
          <label htmlFor="study-mode-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Study Mode
          </label>
          <select
            id="study-mode-select"
            value={form.study_mode}
            onChange={(e) => onChange('study_mode', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {STUDY_MODE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Full-time, part-time, or remote study compatibility.</p>
        </div>

        {/* Funding Preference */}
        <div>
          <label htmlFor="funding-pref-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Funding Preference
          </label>
          <select
            id="funding-pref-select"
            value={form.funding_preference}
            onChange={(e) => onChange('funding_preference', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {FUNDING_PREFERENCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Matched against scholarship coverage types.</p>
        </div>

        {/* Institution Type */}
        <div>
          <label htmlFor="institution-type-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Institution Type
          </label>
          <select
            id="institution-type-select"
            value={form.institution_type}
            onChange={(e) => onChange('institution_type', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {INSTITUTION_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Public vs private university preferences.</p>
        </div>
      </div>
    </div>
  );
};
