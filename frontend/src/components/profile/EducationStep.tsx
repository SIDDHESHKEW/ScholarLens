import React from 'react';
import type { StudentProfileFormState } from '../../types/profile';
import { EDUCATION_LEVEL_OPTIONS, FIELD_OF_STUDY_OPTIONS } from '../../types/profile';

interface EducationStepProps {
  form: StudentProfileFormState;
  onChange: (field: keyof StudentProfileFormState, value: unknown) => void;
  errors: Record<string, string>;
}

export const EducationStep: React.FC<EducationStepProps> = ({ form, onChange, errors }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-white">Academic Background</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Provide your current academic standing and intended field of study. This is the primary driver of the Recommendation Quality Gate.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Education Level */}
        <div>
          <label htmlFor="education-level-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Education Level <span className="text-red-500">*</span>
          </label>
          <select
            id="education-level-select"
            value={form.education_level}
            onChange={(e) => {
              const val = e.target.value;
              onChange('education_level', val);
              if (val === 'school') {
                onChange('gpa', '');
              }
            }}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {EDUCATION_LEVEL_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Filters out conflicting degrees (e.g. PhD positions for undergrads).</p>
        </div>

        {/* Field of Study */}
        <div>
          <label htmlFor="field-of-study-select" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Primary Field of Study <span className="text-red-500">*</span>
          </label>
          <select
            id="field-of-study-select"
            value={form.field_of_study}
            onChange={(e) => onChange('field_of_study', e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {FIELD_OF_STUDY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Disciplines are matched via taxonomy and quality gate.</p>
        </div>

        {/* Custom field if 'other' */}
        {form.field_of_study === 'other' && (
          <div className="sm:col-span-2">
            <label htmlFor="custom-field-input" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
              Specify Your Field of Study <span className="text-red-500">*</span>
            </label>
            <input
              id="custom-field-input"
              type="text"
              value={form.custom_field_of_study}
              onChange={(e) => onChange('custom_field_of_study', e.target.value)}
              placeholder="e.g. Data Science, Robotics, Computational Biology"
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
        )}

        {/* Degree / Program */}
        <div>
          <label htmlFor="degree-input" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Degree / Program Name
          </label>
          <input
            id="degree-input"
            type="text"
            value={form.degree}
            onChange={(e) => onChange('degree', e.target.value)}
            placeholder="e.g. Bachelor of Science in Computer Engineering"
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>

        {/* GPA */}
        {form.education_level !== 'school' && (
          <div>
            <label htmlFor="gpa-input" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
              Cumulative GPA (0.0 – 10.0 Scale)
            </label>
            <input
              id="gpa-input"
              type="number"
              step="any"
              min="0"
              max="10"
              value={form.gpa}
              onChange={(e) => onChange('gpa', e.target.value)}
              placeholder="e.g. 8.5"
              className={`w-full px-3.5 py-2.5 rounded-lg border ${
                errors.gpa
                  ? 'border-red-500 bg-red-50/20 dark:bg-red-950/20'
                  : 'border-slate-300 dark:border-slate-700'
              } bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm`}
            />
            {errors.gpa && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.gpa}</p>}
          </div>
        )}

        {/* Academic Percentage */}
        <div>
          <label htmlFor="percentage-input" className="block text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
            Academic Percentage (0 – 100%)
          </label>
          <input
            id="percentage-input"
            type="number"
            step="0.1"
            min="0"
            max="100"
            value={form.academic_percentage}
            onChange={(e) => onChange('academic_percentage', e.target.value)}
            placeholder="e.g. 88.5"
            className={`w-full px-3.5 py-2.5 rounded-lg border ${
              errors.academic_percentage
                ? 'border-red-500 bg-red-50/20 dark:bg-red-950/20'
                : 'border-slate-300 dark:border-slate-700'
            } bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm`}
          />
          {errors.academic_percentage && (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.academic_percentage}</p>
          )}
        </div>
      </div>
    </div>
  );
};
