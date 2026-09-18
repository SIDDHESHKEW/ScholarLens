import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { App } from '../App';
import * as apiModule from '../services/api';
import type { RecommendationResponse } from '../types/api';

const mockResponse: RecommendationResponse = {
  recommendation_policy_version: 'v1',
  scoring_policy_version: 'v1',
  student_profile_status: 'normalized',
  total_candidates: 604,
  recommended_count: 2,
  recommendations: [
    {
      rank: 1,
      scholarship_id: 61,
      title: 'Electronic Arts (EA) Student Scholarship',
      provider: 'Electronic Arts',
      eligibility: {
        outcome: 'ELIGIBLE',
        unknown_fields: [],
      },
      score: 95.0,
      score_breakdown: [],
      matching_factors: [
        {
          dimension: 'field_of_study',
          status: 'MATCH',
          explanation: 'Curricular alignment',
        },
      ],
      reasons: ['Direct field match'],
      warnings: [],
      verification: {
        status: 'VERIFIED',
        freshness: 'FRESH',
        warnings: [],
      },
      deadline: '2026-12-31',
      application_url: 'https://ea.com/apply',
      official_source_url: 'https://ea.com',
    },
    {
      rank: 2,
      scholarship_id: 101,
      title: 'Hispanic Scholarship Fund Scholar Program',
      provider: 'HSF',
      eligibility: {
        outcome: 'POSSIBLY_ELIGIBLE',
        unknown_fields: ['gpa'],
      },
      score: 86.7,
      score_breakdown: [],
      matching_factors: [
        {
          dimension: 'field_of_study',
          status: 'MATCH',
          explanation: 'Open to all disciplines',
        },
      ],
      reasons: ['Open academic discipline'],
      warnings: [],
      verification: {
        status: 'UNVERIFIED',
        freshness: 'UNKNOWN',
        warnings: [],
      },
      deadline: null,
      application_url: null,
      official_source_url: null,
    },
  ],
  excluded: {
    not_eligible_count: 140,
    not_eligible_ids: [1, 2],
    quality_blocked_count: 128,
    quality_blocked_ids: [37, 297],
  },
};

describe('User Flow & Integration', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders landing page and navigates to prediction form', () => {
    render(<App />);

    expect(screen.getByText(/Find Scholarships You/)).toBeInTheDocument();
    expect(screen.getByText('Actually Qualify For.')).toBeInTheDocument();

    const predictBtns = screen.getAllByText('Predict Your Scholarship');
    fireEvent.click(predictBtns[0]);

    expect(screen.getByText('Tell Us About Your Profile')).toBeInTheDocument();
    expect(screen.getByText('About You')).toBeInTheDocument();
  });

  it('validates required fields on step 1', () => {
    render(<App />);
    const predictBtns = screen.getAllByText('Predict Your Scholarship');
    fireEvent.click(predictBtns[0]);

    const ageInput = screen.getByLabelText(/Age/);
    fireEvent.change(ageInput, { target: { value: '' } });

    const continueBtn = screen.getByText('Continue');
    fireEvent.click(continueBtn);

    expect(screen.getByText(/Please enter a valid age/)).toBeInTheDocument();
  });

  it('navigates through the 5 steps and renders recommendations after submission', async () => {
    const fetchSpy = vi.spyOn(apiModule, 'fetchRecommendations').mockResolvedValue(mockResponse);

    render(<App />);
    const predictBtns = screen.getAllByText('Predict Your Scholarship');
    fireEvent.click(predictBtns[0]);

    // Step 1 -> Step 2
    fireEvent.click(screen.getByText('Continue'));

    // Step 2 -> Step 3
    await waitFor(() => {
      expect(screen.getByText('Academic Background')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Step 3 -> Step 4
    await waitFor(() => {
      expect(screen.getByText('Study Preferences')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Step 4 -> Step 5
    await waitFor(() => {
      expect(screen.getByText('Financial & Additional Criteria')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Step 5 Review
    await waitFor(() => {
      expect(screen.getByText('Review Your Profile')).toBeInTheDocument();
    });

    const submitBtn = screen.getByText('Predict My Scholarships');
    fireEvent.click(submitBtn);

    expect(fetchSpy).toHaveBeenCalledTimes(1);

    // Results Page renders
    await waitFor(() => {
      expect(screen.getByText('Your Recommendation Results')).toBeInTheDocument();
      expect(screen.getByText(/Electronic Arts \(EA\) Student Scholarship/)).toBeInTheDocument();
      expect(screen.getByText(/Hispanic Scholarship Fund/)).toBeInTheDocument();
    });

    // Check Metrics
    expect(screen.getByText('604')).toBeInTheDocument(); // total evaluated
    expect(screen.getByText('128')).toBeInTheDocument(); // quality blocked
    expect(screen.getByText('140')).toBeInTheDocument(); // not eligible
  });
});
