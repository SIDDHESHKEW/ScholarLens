import React from 'react';
import type { StudentProfileFormState } from '../../types/profile';
import { COUNTRY_OPTIONS } from '../../types/profile';

interface BasicInfoStepProps {
  form: StudentProfileFormState;
  onChange: (field: keyof StudentProfileFormState, value: unknown) => void;
  errors: Record<string, string>;
}

export const BasicInfoStep: React.FC<BasicInfoStepProps> = ({ form, onChange, errors }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-white">Personal & Geographic Information</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Tell us about your age and citizenship. These parameters evaluate nationality-specific eligibility criteria.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Age */}
        <div>
          <label htmlFor="age-input" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Age <span className="text-red-500">*</span>
          </label>
          <input
            id="age-input"
            type="number"
            min="10"
            max="100"
            value={form.age}
            onChange={(e) => onChange('age', e.target.value)}
            placeholder="e.g. 20"
            className={`w-full px-3.5 py-2.5 rounded-lg border ${
              errors.age
                ? 'border-red-500 bg-red-50/20 dark:bg-red-950/20'
                : 'border-slate-300 dark:border-slate-700'
            } bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm`}
          />
          {errors.age ? (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.age}</p>
          ) : (
            <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Required for age-bracket eligibility rules.</p>
          )}
        </div>

        {/* Gender */}
        <div>
          <label htmlFor="gender-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Gender / Category Targeting
          </label>
          <select
            id="gender-select"
            value={form.gender}
            onChange={(e) => onChange('gender', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="any">Prefer not to say / Any</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="other">Other</option>
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Used for demographic grants (e.g. Women in STEM).</p>
        </div>

        {/* Nationality */}
        <div>
          <label htmlFor="nationality-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Nationality / Citizenship <span className="text-red-500">*</span>
          </label>
          <select
            id="nationality-select"
            value={form.nationality}
            onChange={(e) => onChange('nationality', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {COUNTRY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Matches country-of-citizenship requirements.</p>
        </div>

        {/* Country of Residence */}
        <div>
          <label htmlFor="residence-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Country of Current Residence
          </label>
          <select
            id="residence-select"
            value={form.residence_country}
            onChange={(e) => onChange('residence_country', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {COUNTRY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Usually matches your current physical location.</p>
        </div>
      </div>
    </div>
  );
};
