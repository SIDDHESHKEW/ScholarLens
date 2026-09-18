import React from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';

interface FinalCTAProps {
  onPredictClick: () => void;
}

export const FinalCTA: React.FC<FinalCTAProps> = ({ onPredictClick }) => {
  return (
    <section className="py-20 bg-gradient-to-b from-slate-50/50 to-blue-50/30 dark:from-slate-900/40 dark:to-blue-950/20 transition-colors">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Start Finding Opportunities</span>
        </div>

        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Ready to discover scholarships tailored to your academic journey?
        </h2>

        <p className="text-slate-600 dark:text-slate-300 text-base sm:text-lg max-w-2xl mx-auto">
          Take 2 minutes to enter your profile. Our engine runs an instant multi-dimensional eligibility and ranking analysis.
        </p>

        <div className="pt-2">
          <button
            onClick={onPredictClick}
            className="inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-bold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 rounded-xl shadow-lg shadow-blue-600/25 transition-all transform hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
          >
            <span>Predict Your Scholarship</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </section>
  );
};
