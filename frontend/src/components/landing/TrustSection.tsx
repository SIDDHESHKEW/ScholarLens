import React from 'react';
import { AlertCircle, HelpCircle, CheckCircle2, ShieldAlert } from 'lucide-react';

export const TrustSection: React.FC = () => {
  return (
    <section className="py-20 bg-white dark:bg-slate-950 border-b border-slate-200/80 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto bg-slate-900 rounded-3xl p-8 sm:p-12 text-white shadow-xl relative overflow-hidden">
          {/* Subtle background glow */}
          <div className="absolute -right-20 -top-20 w-80 h-80 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-700">
              <ShieldAlert className="w-3.5 h-3.5 text-blue-400" />
              <span>Core Trust & Transparency Principles</span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Honest Data Semantics: What Our Labels Mean
            </h2>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              ScholarMatch never exaggerates your chances or conceals missing requirements. 
              We distinguish strictly between confirmed eligibility and unverified data.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
              <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700 space-y-1.5">
                <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>ELIGIBLE</span>
                </div>
                <p className="text-xs text-slate-400">
                  Every hard rule and evidence condition passed against your profile.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700 space-y-1.5">
                <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
                  <AlertCircle className="w-4 h-4" />
                  <span>POSSIBLY ELIGIBLE</span>
                </div>
                <p className="text-xs text-slate-400">
                  No criteria failed, but certain requirements could not be confirmed due to missing source data.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700 space-y-1.5">
                <div className="flex items-center gap-2 text-slate-300 font-bold text-sm">
                  <HelpCircle className="w-4 h-4 text-blue-400" />
                  <span>UNKNOWN ≠ PASS</span>
                </div>
                <p className="text-xs text-slate-400">
                  Missing information is never treated as a pass when contradictory evidence exists.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
