import React, { useState } from 'react';
import type { StudentProfileFormState } from './types/profile';
import type { RecommendationResponse } from './types/api';
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { Loader } from './components/common/Loader';
import { EmptyState } from './components/results/EmptyState';
import { LandingPage } from './pages/LandingPage';
import { PredictPage } from './pages/PredictPage';
import { ResultsPage } from './pages/ResultsPage';
import { buildRecommendationRequest } from './services/adapter';
import { fetchRecommendations, ApiError } from './services/api';
import { useTheme } from './hooks/useTheme';

export const App: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [currentPage, setCurrentPage] = useState<'landing' | 'predict' | 'results'>('landing');
  const [lastForm, setLastForm] = useState<StudentProfileFormState | null>(null);
  const [lastLimit, setLastLimit] = useState(5);
  const [lastIncludePossiblyEligible, setLastIncludePossiblyEligible] = useState(true);
  const [recommendationResponse, setRecommendationResponse] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredictSubmit = async (
    form: StudentProfileFormState,
    limit: number,
    includePossiblyEligible: boolean
  ) => {
    setLastForm(form);
    setLastLimit(limit);
    setLastIncludePossiblyEligible(includePossiblyEligible);
    setIsLoading(true);
    setError(null);

    const requestPayload = buildRecommendationRequest(form, limit, includePossiblyEligible);

    try {
      const response = await fetchRecommendations(requestPayload);
      setRecommendationResponse(response);
      setCurrentPage('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred while communicating with the engine.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (lastForm) {
      handlePredictSubmit(lastForm, lastLimit, lastIncludePossiblyEligible);
    } else {
      setCurrentPage('predict');
      setError(null);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50/50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans selection:bg-blue-100 dark:selection:bg-blue-900 selection:text-blue-900 dark:selection:text-blue-100 transition-colors">
      <Navbar
        onNavigate={(page) => {
          setError(null);
          setCurrentPage(page);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        currentPage={currentPage}
        hasResults={!!recommendationResponse}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      <main className="flex-1">
        {isLoading ? (
          <div className="py-20 px-4 max-w-xl mx-auto">
            <Loader />
          </div>
        ) : error ? (
          <div className="py-16 px-4">
            <EmptyState
              type="error"
              errorMessage={error}
              onRetry={handleRetry}
              onEditProfile={() => {
                setError(null);
                setCurrentPage('predict');
              }}
            />
          </div>
        ) : currentPage === 'landing' ? (
          <LandingPage onPredictClick={() => setCurrentPage('predict')} />
        ) : currentPage === 'predict' ? (
          <PredictPage onSubmit={handlePredictSubmit} isSubmitting={isLoading} />
        ) : currentPage === 'results' && recommendationResponse ? (
          <ResultsPage
            response={recommendationResponse}
            onEditProfile={() => setCurrentPage('predict')}
            onRefresh={handleRetry}
          />
        ) : (
          <LandingPage onPredictClick={() => setCurrentPage('predict')} />
        )}
      </main>

      <Footer
        onNavigate={(page) => {
          setError(null);
          setCurrentPage(page);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
      />
    </div>
  );
};

export default App;
