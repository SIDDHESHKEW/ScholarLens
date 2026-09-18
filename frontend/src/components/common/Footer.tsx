import React from 'react';
import { Compass, ShieldCheck } from 'lucide-react';

interface FooterProps {
  onNavigate: (page: 'landing' | 'predict' | 'results') => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="bg-slate-900 dark:bg-slate-950 text-slate-400 py-12 border-t border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-md bg-blue-600 flex items-center justify-center text-white">
                <Compass className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                Scholar<span className="text-blue-400">Match</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-md leading-relaxed">
              ScholarMatch: Scholarship Finder and Eligibility Predictor. Evaluating hard eligibility, 
              academic discipline relevance, and multi-dimensional preference compatibility.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
              Navigation
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <button
                  onClick={() => onNavigate('landing')}
                  className="hover:text-white transition-colors"
                >
                  Home
                </button>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-white transition-colors">
                  How It Works
                </a>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('predict')}
                  className="hover:text-white transition-colors"
                >
                  Predict Scholarship
                </button>
              </li>
            </ul>
          </div>

          {/* Architecture */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
              Engine Principles
            </h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Eligibility-First Pipeline</span>
              </li>
              <li className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-blue-400" />
                <span>Explainable 100pt Scoring</span>
              </li>
              <li className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-purple-400" />
                <span>Quality Gate Filtration</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Transparency note */}
        <div className="pt-8 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <p className="max-w-2xl text-center md:text-left">
            <strong className="text-slate-300">Data & Transparency Notice:</strong> ScholarMatch recommendations 
            are strictly based on available scholarship data and evaluated eligibility evidence. 
            Availability, requirements, deadlines, and funding remain subject to provider verification.
          </p>
          <p>© {new Date().getFullYear()} ScholarMatch. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};
