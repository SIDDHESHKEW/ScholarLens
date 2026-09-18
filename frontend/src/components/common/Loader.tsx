import React, { useEffect, useState } from 'react';
import { Loader2, ShieldCheck, CheckCircle2 } from 'lucide-react';

const STEPS = [
  'Analyzing your academic profile...',
  'Checking hard eligibility & contradiction evidence...',
  'Evaluating multi-dimensional matching factors...',
  'Applying Recommendation Quality Gate...',
  'Preparing explainable ranking...',
];

export const Loader: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 600);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-[420px] flex flex-col items-center justify-center p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-full bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-blue-600 dark:text-blue-400 animate-spin" />
        </div>
        <div className="absolute -bottom-1 -right-1 bg-emerald-500 rounded-full p-1 text-white shadow-sm">
          <ShieldCheck className="w-4 h-4" />
        </div>
      </div>

      <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
        Evaluating Opportunities
      </h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mb-8">
        ScholarMatch is comparing your profile against the scholarship database using deterministic eligibility rules and explainable scoring.
      </p>

      {/* Step progression display */}
      <div className="w-full max-w-md space-y-2.5 text-left">
        {STEPS.map((step, idx) => {
          const isDone = idx < currentStepIndex;
          const isCurrent = idx === currentStepIndex;

          return (
            <div
              key={step}
              className={`flex items-center gap-3 p-2.5 rounded-lg text-xs font-medium transition-all duration-300 ${
                isCurrent
                  ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-900 dark:text-blue-200 border border-blue-200 dark:border-blue-800'
                  : isDone
                  ? 'text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-750'
                  : 'text-slate-400 dark:text-slate-600 opacity-60'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-spin shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-300 dark:border-slate-700 shrink-0" />
              )}
              <span>{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
