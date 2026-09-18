import React from 'react';
import type { StudentProfileFormState } from '../../types/profile';
import { CURRENCY_OPTIONS } from '../../types/profile';

interface AdditionalStepProps {
  form: StudentProfileFormState;
  onChange: (field: keyof StudentProfileFormState, value: unknown) => void;
  errors: Record<string, string>;
}

export const AdditionalStep: React.FC<AdditionalStepProps> = ({ form, onChange, errors }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-white">Financial & Additional Criteria</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Optional attributes to evaluate need-based and inclusion-specific scholarship opportunities.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Family Income Amount */}
        <div>
          <label htmlFor="income-input" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Annual Household Income (Optional)
          </label>
          <input
            id="income-input"
            type="number"
            min="0"
            step="1000"
            value={form.family_income}
            onChange={(e) => onChange('family_income', e.target.value)}
            placeholder="e.g. 35000"
            className={`w-full px-3.5 py-2.5 rounded-lg border ${
              errors.family_income
                ? 'border-red-500 bg-red-50/20 dark:bg-red-950/20'
                : 'border-slate-300 dark:border-slate-700'
            } bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm`}
          />
          {errors.family_income ? (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.family_income}</p>
          ) : (
            <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Used for need-based income thresholds.</p>
          )}
        </div>

        {/* Currency */}
        <div>
          <label htmlFor="currency-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Income Currency
          </label>
          <select
            id="currency-select"
            value={form.family_income_currency}
            onChange={(e) => onChange('family_income_currency', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {CURRENCY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Currency is preserved directly without arbitrary conversion.</p>
        </div>

        {/* Disability Status */}
        <div className="sm:col-span-2 pt-2">
          <label className="flex items-start gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors">
            <input
              type="checkbox"
              checked={form.disability_status}
              onChange={(e) => onChange('disability_status', e.target.checked)}
              className="mt-0.5 w-4 h-4 rounded text-blue-600 border-slate-300 dark:border-slate-700 focus:ring-blue-500 bg-white dark:bg-slate-800"
            />
            <div>
              <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Inclusion / Disability Eligibility
              </span>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Check this if you are eligible for accessibility and special assistance scholarship schemes.
              </p>
            </div>
          </label>
        </div>
      </div>
    </div>
  );
};
