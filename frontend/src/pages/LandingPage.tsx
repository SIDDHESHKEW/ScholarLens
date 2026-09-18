import React from 'react';
import { HeroSection } from '../components/landing/HeroSection';
import { HowItWorks } from '../components/landing/HowItWorks';
import { WhyScholarMatch } from '../components/landing/WhyScholarMatch';
import { TrustSection } from '../components/landing/TrustSection';
import { FinalCTA } from '../components/landing/FinalCTA';

interface LandingPageProps {
  onPredictClick: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onPredictClick }) => {
  return (
    <div className="space-y-0">
      <HeroSection onPredictClick={onPredictClick} />
      <HowItWorks />
      <WhyScholarMatch />
      <TrustSection />
      <FinalCTA onPredictClick={onPredictClick} />
    </div>
  );
};
