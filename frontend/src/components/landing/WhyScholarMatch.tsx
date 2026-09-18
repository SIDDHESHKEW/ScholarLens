import React from 'react';
import { ShieldCheck, BarChart3, Filter, FileText } from 'lucide-react';

export const WhyScholarMatch: React.FC = () => {
  const features = [
    {
      title: 'Eligibility First',
      desc: 'Scholarships are evaluated against hard rules and contradiction evidence. Ineligible opportunities are strictly blocked before recommendation ranking.',
      icon: ShieldCheck,
      badge: 'Rigorous Rules',
    },
    {
      title: 'Explainable 100pt Scoring',
      desc: 'Every recommendation includes a multi-dimensional score breakdown across Field of Study, Country, Mode, and Funding. No black-box scores.',
      icon: BarChart3,
      badge: 'Zero Black Boxes',
    },
    {
      title: 'Discipline Quality Gate',
      desc: 'Our Recommendation Quality Gate prevents irrelevant opportunities (like humanities language grants for CS students) from floating to the top.',
      icon: Filter,
      badge: 'Quality Enforced',
    },
    {
      title: 'Transparent Provenance',
      desc: 'Every scholarship card surfaces its verification status, freshness, and data quality warnings so you know exactly where the data originates.',
      icon: FileText,
      badge: 'Honest Data',
    },
  ];

  return (
    <section id="why-scholarmatch" className="py-20 bg-slate-50/60 dark:bg-slate-900/40 border-b border-slate-200/80 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-3 py-1 rounded-full border border-blue-200 dark:border-blue-800">
            Why ScholarMatch
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Built for Integrity, Not Artificial Hype
          </h2>
          <p className="text-slate-600 dark:text-slate-300 text-base sm:text-lg">
            Unlike platforms that make unsupportable approval guarantees, ScholarMatch focuses on mathematical precision, hard eligibility compliance, and complete transparency.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feat) => {
            const Icon = feat.icon;
            return (
              <div
                key={feat.title}
                className="p-8 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 shadow-sm hover:shadow-md transition-all flex flex-col sm:flex-row gap-5"
              >
                <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-950/60 border border-blue-100 dark:border-blue-800 flex items-center justify-center text-blue-600 dark:text-blue-400 shrink-0">
                  <Icon className="w-6 h-6" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white">{feat.title}</h3>
                    <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                      {feat.badge}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                    {feat.desc}
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

export const WhyScholarLens = WhyScholarMatch;
