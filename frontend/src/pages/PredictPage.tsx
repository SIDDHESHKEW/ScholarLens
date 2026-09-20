import React, { useState } from 'react';
import type { StudentProfileFormState } from '../types/profile';
import { INITIAL_FORM_STATE } from '../types/profile';
import { generateRandomProfile } from '../services/randomProfile';
import { StepIndicator } from '../components/profile/StepIndicator';
import { BasicInfoStep } from '../components/profile/BasicInfoStep';
import { EducationStep } from '../components/profile/EducationStep';
import { PreferencesStep } from '../components/profile/PreferencesStep';
import { AdditionalStep } from '../components/profile/AdditionalStep';
import { ReviewStep } from '../components/profile/ReviewStep';
import { ArrowLeft, ArrowRight, Dices, Sparkles } from 'lucide-react';

interface PredictPageProps {
  onSubmit: (form: StudentProfileFormState, limit: number, includePossiblyEligible: boolean) => void;
  isSubmitting: boolean;
}

const STEP_NAMES = ['About You', 'Education', 'Preferences', 'Additional', 'Review'];

export const PredictPage: React.FC<PredictPageProps> = ({ onSubmit, isSubmitting }) => {
  const [form, setForm] = useState<StudentProfileFormState>(INITIAL_FORM_STATE);
  const [currentStep, setCurrentStep] = useState(1);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [includePossiblyEligible, setIncludePossiblyEligible] = useState(true);
  const [limit, setLimit] = useState(5);
  const [randomNotice, setRandomNotice] = useState(false);

  const handleFieldChange = (field: keyof StudentProfileFormState, value: unknown) => {
    setForm((prev) => {
      const updated = { ...prev, [field]: value };
      if (field === 'education_level' && value === 'school') {
        updated.gpa = '';
      }
      return updated;
    });
    if (errors[field]) {
      setErrors((prev) => {
        const copy = { ...prev };
        delete copy[field];
        return copy;
      });
    }
    if (field === 'education_level' && value === 'school' && errors.gpa) {
      setErrors((prev) => {
        const copy = { ...prev };
        delete copy.gpa;
        return copy;
      });
    }
  };

  const handleFillRandomProfile = () => {
    const newProfile = generateRandomProfile();
    setForm(newProfile);
    setErrors({});
    setRandomNotice(true);
    setCurrentStep(5);
  };

  const validateStep = (step: number): boolean => {
    const errs: Record<string, string> = {};

    if (step === 1) {
      const ageNum = parseInt(form.age, 10);
      if (!form.age.trim() || isNaN(ageNum) || ageNum < 10 || ageNum > 100) {
        errs.age = 'Please enter a valid age between 10 and 100.';
      }
      if (!form.nationality.trim()) {
        errs.nationality = 'Nationality is required.';
      }
    } else if (step === 2) {
      if (!form.education_level.trim()) {
        errs.education_level = 'Education level is required.';
      }
      if (!form.field_of_study.trim()) {
        errs.field_of_study = 'Field of study is required.';
      }
      if (form.field_of_study === 'other' && !form.custom_field_of_study.trim()) {
        errs.custom_field_of_study = 'Please specify your field of study.';
      }
      if (form.education_level !== 'school' && form.gpa.trim()) {
        const gpa = parseFloat(form.gpa);
        if (isNaN(gpa) || gpa < 0 || gpa > 10.0) {
          errs.gpa = 'GPA must be between 0.0 and 10.0.';
        }
      }
      if (form.academic_percentage.trim()) {
        const pct = parseFloat(form.academic_percentage);
        if (isNaN(pct) || pct < 0 || pct > 100) {
          errs.academic_percentage = 'Percentage must be between 0% and 100%.';
        }
      }
    } else if (step === 3) {
      if (!form.preferred_study_country.trim()) {
        errs.preferred_study_country = 'Preferred destination country is required.';
      }
    } else if (step === 4) {
      if (form.family_income.trim()) {
        const inc = parseFloat(form.family_income);
        if (isNaN(inc) || inc < 0) {
          errs.family_income = 'Income must be a valid positive number.';
        }
      }
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, 5));
    }
  };

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = () => {
    if (validateStep(1) && validateStep(2) && validateStep(3) && validateStep(4)) {
      onSubmit(form, limit, includePossiblyEligible);
    }
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      {/* Header & Fill Random Profile action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Tell Us About Your Profile
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            ScholarMatch matches your background and preferences against verified database criteria.
          </p>
        </div>

        <div className="flex flex-col items-start sm:items-end gap-1 shrink-0">
          <button
            type="button"
            onClick={handleFillRandomProfile}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/70 hover:bg-blue-100 dark:hover:bg-blue-900/60 border border-blue-200 dark:border-blue-800 shadow-sm transition-all active:scale-95"
            title="Generate a sample profile for testing"
          >
            <Dices className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Fill Random Profile</span>
          </button>
          <span className="text-[11px] text-slate-400 dark:text-slate-500">
            Generate a sample profile for testing
          </span>
        </div>
      </div>

      {/* Random Profile Notification Notice */}
      {randomNotice && (
        <div className="mb-6 p-3.5 rounded-xl bg-blue-50/90 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-800 text-xs text-blue-900 dark:text-blue-300 flex items-center justify-between gap-2 shadow-sm">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0" />
            <span>Random test profile generated — review the details before predicting.</span>
          </div>
          <button
            type="button"
            onClick={() => setRandomNotice(false)}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 font-bold text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Form Container */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 sm:p-10 transition-colors">
        <StepIndicator
          currentStep={currentStep}
          totalSteps={5}
          stepNames={STEP_NAMES}
          onStepClick={(step) => {
            if (step < currentStep || validateStep(currentStep)) {
              setCurrentStep(step);
            }
          }}
        />

        {/* Step Views */}
        <div className="mt-8">
          {currentStep === 1 && (
            <BasicInfoStep form={form} onChange={handleFieldChange} errors={errors} />
          )}

          {currentStep === 2 && (
            <EducationStep form={form} onChange={handleFieldChange} errors={errors} />
          )}

          {currentStep === 3 && (
            <PreferencesStep form={form} onChange={handleFieldChange} />
          )}

          {currentStep === 4 && (
            <AdditionalStep form={form} onChange={handleFieldChange} errors={errors} />
          )}

          {currentStep === 5 && (
            <ReviewStep
              form={form}
              onEdit={() => setCurrentStep(1)}
              onSubmit={handleSubmit}
              includePossiblyEligible={includePossiblyEligible}
              onToggleIncludePossiblyEligible={setIncludePossiblyEligible}
              limit={limit}
              onLimitChange={setLimit}
              isSubmitting={isSubmitting}
            />
          )}
        </div>

        {/* Navigation Buttons for Steps 1 - 4 */}
        {currentStep < 5 && (
          <div className="mt-10 pt-6 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <button
              type="button"
              onClick={handleBack}
              disabled={currentStep === 1}
              className={`inline-flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                currentStep === 1
                  ? 'text-slate-300 dark:text-slate-700 cursor-not-allowed'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              type="button"
              onClick={handleNext}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
            >
              <span>Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
