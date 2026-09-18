import React, { useState } from 'react';
import { Compass, Menu, X, Sun, Moon } from 'lucide-react';
import type { Theme } from '../../hooks/useTheme';

interface NavbarProps {
  onNavigate: (page: 'landing' | 'predict' | 'results') => void;
  currentPage: 'landing' | 'predict' | 'results';
  hasResults: boolean;
  theme: Theme;
  onToggleTheme: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onNavigate,
  currentPage,
  hasResults,
  theme,
  onToggleTheme,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNav = (page: 'landing' | 'predict' | 'results') => {
    onNavigate(page);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <button
            onClick={() => handleNav('landing')}
            className="flex items-center gap-2.5 text-left focus:outline-none focus:ring-2 focus:ring-blue-600 rounded-lg p-1"
          >
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/30">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
                Scholar<span className="text-blue-600 dark:text-blue-400">Match</span>
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                v1.0
              </span>
            </div>
          </button>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-8">
            <button
              onClick={() => handleNav('landing')}
              className={`text-sm font-medium transition-colors ${
                currentPage === 'landing'
                  ? 'text-blue-600 dark:text-blue-400 font-bold'
                  : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Home
            </button>
            <a
              href="#how-it-works"
              onClick={(e) => {
                if (currentPage !== 'landing') {
                  e.preventDefault();
                  handleNav('landing');
                  setTimeout(() => {
                    document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
                  }, 100);
                }
              }}
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              How It Works
            </a>
            <a
              href="#why-scholarmatch"
              onClick={(e) => {
                if (currentPage !== 'landing') {
                  e.preventDefault();
                  handleNav('landing');
                  setTimeout(() => {
                    document.getElementById('why-scholarmatch')?.scrollIntoView({ behavior: 'smooth' });
                  }, 100);
                }
              }}
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              Why ScholarMatch
            </a>
            {hasResults && (
              <button
                onClick={() => handleNav('results')}
                className={`text-sm font-medium transition-colors ${
                  currentPage === 'results'
                    ? 'text-blue-600 dark:text-blue-400 font-bold'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Results
              </button>
            )}
          </nav>

          {/* Desktop Actions: Theme Toggle + CTA */}
          <div className="hidden md:flex items-center gap-3">
            {/* Theme Toggle Button */}
            <button
              onClick={onToggleTheme}
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-slate-700" />
              )}
            </button>

            <button
              onClick={() => handleNav('predict')}
              className="inline-flex items-center justify-center px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 rounded-lg shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
            >
              Predict Your Scholarship
            </button>
          </div>

          {/* Mobile Actions: Theme Toggle + Hamburger */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={onToggleTheme}
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 transition-colors"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-slate-700" />
              )}
            </button>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle navigation menu"
              className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 pt-3 pb-5 space-y-3 transition-colors">
          <button
            onClick={() => handleNav('landing')}
            className="block w-full text-left py-2 text-base font-medium text-slate-800 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400"
          >
            Home
          </button>
          <a
            href="#how-it-works"
            onClick={() => setMobileMenuOpen(false)}
            className="block w-full text-left py-2 text-base font-medium text-slate-800 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400"
          >
            How It Works
          </a>
          <a
            href="#why-scholarmatch"
            onClick={() => setMobileMenuOpen(false)}
            className="block w-full text-left py-2 text-base font-medium text-slate-800 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400"
          >
            Why ScholarMatch
          </a>
          {hasResults && (
            <button
              onClick={() => handleNav('results')}
              className="block w-full text-left py-2 text-base font-medium text-slate-800 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400"
            >
              View Matches
            </button>
          )}
          <button
            onClick={() => handleNav('predict')}
            className="w-full mt-2 py-2.5 px-4 text-center font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm"
          >
            Predict Your Scholarship
          </button>
        </div>
      )}
    </header>
  );
};
