import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PredictPage } from '../pages/PredictPage';
import { generateRandomProfile } from '../services/randomProfile';
import { ScholarshipCard } from '../components/results/ScholarshipCard';
import type { RecommendationItem } from '../types/api';

describe('Pre-Phase 12 UI/UX Refinement Tests', () => {
  describe('Change 1: Random Profile Generator & Direct Review Navigation', () => {
    it('generates a valid schema-compliant profile with realistic values', () => {
      const profile = generateRandomProfile();

      expect(parseInt(profile.age, 10)).toBeGreaterThanOrEqual(14);
      expect(parseInt(profile.age, 10)).toBeLessThanOrEqual(50);
      expect(profile.nationality).toBeTruthy();
      expect(profile.residence_country).toBeTruthy();
      expect(profile.education_level).toBeTruthy();
      expect(profile.field_of_study).toBeTruthy();
      expect(profile.degree).toBeTruthy();
      expect(profile.preferred_study_country).toBeTruthy();
      expect(profile.study_mode).toBeTruthy();
      expect(profile.funding_preference).toBeTruthy();
    });

    it('generates different random profiles on subsequent invocations', () => {
      const p1 = generateRandomProfile();
      let different = false;

      // Run up to 5 times to ensure stochastic variance
      for (let i = 0; i < 5; i++) {
        const p2 = generateRandomProfile();
        if (
          p1.age !== p2.age ||
          p1.education_level !== p2.education_level ||
          p1.field_of_study !== p2.field_of_study ||
          p1.preferred_study_country !== p2.preferred_study_country
        ) {
          different = true;
          break;
        }
      }
      expect(different).toBe(true);
    });

    it('renders "Fill Random Profile" button and helper text on PredictPage', () => {
      const onSubmit = vi.fn();
      render(<PredictPage onSubmit={onSubmit} isSubmitting={false} />);

      const randomBtn = screen.getByText('Fill Random Profile');
      expect(randomBtn).toBeInTheDocument();
      expect(screen.getByText('Generate a sample profile for testing')).toBeInTheDocument();
    });

    it('clicking "Fill Random Profile" navigates directly to Review step with notice and WITHOUT auto-submitting', () => {
      const onSubmit = vi.fn();
      render(<PredictPage onSubmit={onSubmit} isSubmitting={false} />);

      const randomBtn = screen.getByText('Fill Random Profile');
      fireEvent.click(randomBtn);

      // Direct navigation to Review Step
      expect(screen.getByText('Review Your Profile')).toBeInTheDocument();
      expect(screen.getByText(/Verify your parameters before running the evaluation\./i)).toBeInTheDocument();

      // Notification banner appears
      expect(screen.getByText(/Random test profile generated — review the details before predicting\./i)).toBeInTheDocument();

      // Submit was NOT automatically called
      expect(onSubmit).not.toHaveBeenCalled();

      // Default result limit on review step is 5
      const limitSelect = screen.getByLabelText(/Result Limit:/i) as HTMLSelectElement;
      expect(limitSelect.value).toBe('5');

      // User can click "Edit Profile" to return to step 1 and view/modify fields
      const editBtn = screen.getByText('Edit Profile');
      fireEvent.click(editBtn);

      expect(screen.getByText('Tell Us About Your Profile')).toBeInTheDocument();
      const ageInput = screen.getByLabelText(/Age/i) as HTMLInputElement;
      expect(parseInt(ageInput.value, 10)).toBeGreaterThan(0);
    });

    it('submits prediction with default limit = 5 when user clicks Predict My Scholarships', () => {
      const onSubmit = vi.fn();
      render(<PredictPage onSubmit={onSubmit} isSubmitting={false} />);

      // Fill random profile
      fireEvent.click(screen.getByText('Fill Random Profile'));

      // Click Predict My Scholarships
      const submitBtn = screen.getByText('Predict My Scholarships');
      fireEvent.click(submitBtn);

      expect(onSubmit).toHaveBeenCalledTimes(1);
      // Args: (form, limit, includePossiblyEligible)
      expect(onSubmit.mock.calls[0][1]).toBe(5);
      expect(onSubmit.mock.calls[0][2]).toBe(true);
    });
  });

  describe('Change 2: Step Navigation & State Preservation (No Reload/Jump)', () => {
    it('navigates forward and back while preserving entered and randomized form values', () => {
      const onSubmit = vi.fn();
      render(<PredictPage onSubmit={onSubmit} isSubmitting={false} />);

      // Fill age with custom value
      const ageInput = screen.getByLabelText(/Age/i) as HTMLInputElement;
      fireEvent.change(ageInput, { target: { value: '23' } });

      // Click Continue to step 2 (Education)
      const continueBtn = screen.getByText('Continue');
      fireEvent.click(continueBtn);

      expect(screen.getByText('Academic Background')).toBeInTheDocument();

      // Click Back to step 1
      const backBtn = screen.getByText('Back');
      fireEvent.click(backBtn);

      // Verify age remains 23
      const ageInputAfter = screen.getByLabelText(/Age/i) as HTMLInputElement;
      expect(ageInputAfter.value).toBe('23');
    });
  });

  describe('Change 3: Primary Application Action at TOP of ScholarshipCard', () => {
    const baseMockItem: RecommendationItem = {
      rank: 1,
      scholarship_id: 205,
      title: 'Global Engineering Excellence Grant',
      provider: 'World Engineering Board',
      eligibility: {
        outcome: 'ELIGIBLE',
        unknown_fields: [],
      },
      score: 88.5,
      score_breakdown: [],
      matching_factors: [
        {
          dimension: 'field_of_study',
          status: 'MATCH',
          explanation: 'Engineering matches target',
        },
        {
          dimension: 'study_country',
          status: 'MATCH',
          explanation: 'USA matches destination',
        },
      ],
      reasons: ['Engineering specialization match'],
      warnings: ['This scholarship has not yet been independently verified.'],
      verification: {
        status: 'UNVERIFIED',
        freshness: 'UNKNOWN',
        warnings: ['This scholarship has not yet been independently verified.'],
      },
      deadline: '2026-11-30',
      application_url: 'https://example.org/apply',
      official_source_url: 'https://example.org',
    };

    it('renders primary "Visit Official Application Portal" at top when application_url is present', () => {
      render(<ScholarshipCard item={baseMockItem} onSelect={() => {}} />);

      expect(screen.getByText('#1')).toBeInTheDocument();
      expect(screen.getByText('88.5 / 100')).toBeInTheDocument();
      expect(screen.getByText('Global Engineering Excellence Grant')).toBeInTheDocument();
      
      const appLink = screen.getByText('Visit Official Application Portal').closest('a');
      expect(appLink).toHaveAttribute('href', 'https://example.org/apply');
      expect(appLink).toHaveAttribute('target', '_blank');

      // Secondary evaluation action in footer
      expect(screen.getByText('View Full Evaluation Details')).toBeInTheDocument();
    });

    it('renders "View Official Source" when application_url is missing but official_source_url exists', () => {
      const sourceOnlyItem: RecommendationItem = {
        ...baseMockItem,
        application_url: null,
        official_source_url: 'https://example.org/source',
      };

      render(<ScholarshipCard item={sourceOnlyItem} onSelect={() => {}} />);

      const sourceLink = screen.getByText('View Official Source').closest('a');
      expect(sourceLink).toHaveAttribute('href', 'https://example.org/source');
      expect(screen.queryByText('Visit Official Application Portal')).not.toBeInTheDocument();
    });

    it('renders "Official application link not provided." when neither URL is present', () => {
      const noUrlItem: RecommendationItem = {
        ...baseMockItem,
        application_url: null,
        official_source_url: null,
      };

      render(<ScholarshipCard item={noUrlItem} onSelect={() => {}} />);

      expect(screen.getByText('Official application link not provided.')).toBeInTheDocument();
      expect(screen.queryByText('Visit Official Application Portal')).not.toBeInTheDocument();
      expect(screen.queryByText('View Official Source')).not.toBeInTheDocument();
    });
  });
});
