import React from 'react';
import { UserCheck, ShieldCheck, Sliders, Award } from 'lucide-react';

export const HowItWorks: React.FC = () => {
  const steps = [
    {
      num: '01',
      title: 'Build Your Profile',
      desc: 'Provide your education level, field of study, country preferences, and study mode without unnecessary personal data.',
      icon: UserCheck,
      color: 'bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    },
    {
      num: '02',
      title: 'Check Eligibility First',
      desc: 'Hard requirements and contradictory evidence are evaluated before recommendations. Disqualified opportunities are filtered out.',
      icon: ShieldCheck,
      color: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
    },
    {
      num: '03',
      title: 'Match Preferences',
      desc: 'Our Recommendation Quality Gate compares your exact discipline, preferred study location, and funding preference.',
      icon: Sliders,
      color: 'bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-800',
    },
    {
      num: '04',
      title: 'Discover Scholarships',
      desc: 'Receive transparent, explainable recommendations scored out of 100 with clear reasons, factor breakdowns, and official URLs.',
      icon: Award,
      color: 'bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800',
    },
  ];

  return (
    <section id="how-it-works" className="py-20 bg-white dark:bg-slate-950 border-b border-slate-200/80 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-3 py-1 rounded-full border border-blue-200 dark:border-blue-800">
            Methodology
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            How ScholarMatch Works
          </h2>
          <p className="text-slate-600 dark:text-slate-300 text-base sm:text-lg">
            A deterministic, 4-stage pipeline designed to ensure you only spend time on scholarships you are genuinely compatible with.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <div
                key={step.num}
                className="relative p-6 bg-slate-50/70 dark:bg-slate-900 hover:bg-white dark:hover:bg-slate-800 rounded-2xl border border-slate-200/90 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all hover:shadow-lg hover:-translate-y-1 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-5">
                    <span className="text-2xl font-black text-slate-300 dark:text-slate-700 font-mono">
                      {step.num}
                    </span>
                    <div className={`p-3 rounded-xl border ${step.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                    {step.title}
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                    {step.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
