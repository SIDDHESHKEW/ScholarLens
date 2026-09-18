import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Badge } from '../components/common/Badge';
import { ScholarshipCard } from '../components/results/ScholarshipCard';
import { ScholarshipDetailsModal } from '../components/results/ScholarshipDetailsModal';
import { EmptyState } from '../components/results/EmptyState';
import type { RecommendationItem } from '../types/api';

const mockItemEligible: RecommendationItem = {
  rank: 1,
  scholarship_id: 61,
  title: 'Electronic Arts (EA) Student Scholarship',
  provider: 'Electronic Arts',
  eligibility: {
    outcome: 'ELIGIBLE',
    unknown_fields: [],
  },
  score: 95.0,
  score_breakdown: [
    {
      dimension: 'field_of_study',
      status: 'MATCH',
      weight: 30,
      contribution: 30.0,
      explanation: 'Field matches student field',
    },
  ],
  matching_factors: [
    {
      dimension: 'field_of_study',
      student_value: 'computer_science',
      scholarship_value: 'computer_science',
      status: 'MATCH',
      explanation: 'Direct curriculum match',
    },
    {
      dimension: 'study_mode',
      student_value: 'full_time',
      scholarship_value: 'full_time',
      status: 'MATCH',
      explanation: 'Full-time study confirmed',
    },
  ],
  reasons: ['Direct discipline match for computer science', 'Eligible undergraduate status'],
  warnings: ['UNVERIFIED: Secondary source record'],
  verification: {
    status: 'UNVERIFIED',
    freshness: 'FRESH',
    warnings: ['Source unverified'],
  },
  deadline: '2026-12-31',
  application_url: 'https://ea.com/scholarships/apply',
  official_source_url: 'https://ea.com/scholarships',
};

const mockItemNullScore: RecommendationItem = {
  rank: 2,
  scholarship_id: 62,
  title: 'Unscored Open Scholarship',
  provider: null,
  eligibility: {
    outcome: 'POSSIBLY_ELIGIBLE',
    unknown_fields: ['gpa_minimum'],
  },
  score: null,
  score_breakdown: [],
  matching_factors: [
    {
      dimension: 'funding_preference',
      status: 'MISMATCH',
      explanation: 'Partial funding only',
    },
    {
      dimension: 'language',
      status: 'UNKNOWN',
      explanation: 'Language requirement not specified',
    },
  ],
  reasons: [],
  warnings: [],
  verification: {
    status: 'NEEDS_REVIEW',
    freshness: 'UNKNOWN',
    warnings: [],
  },
  deadline: null,
  application_url: null,
  official_source_url: null,
};

describe('Component Testing', () => {
  it('renders Badge for ELIGIBLE, POSSIBLY_ELIGIBLE, and NOT_ELIGIBLE correctly', () => {
    const { rerender } = render(<Badge status="ELIGIBLE" />);
    expect(screen.getByText('Eligible')).toBeInTheDocument();

    rerender(<Badge status="POSSIBLY_ELIGIBLE" />);
    expect(screen.getByText('Possibly Eligible')).toBeInTheDocument();

    rerender(<Badge status="NOT_ELIGIBLE" />);
    expect(screen.getByText('Not Eligible')).toBeInTheDocument();
  });

  it('renders Badge for matching factors correctly (MATCH, MISMATCH, UNKNOWN)', () => {
    const { rerender } = render(<Badge status="MATCH" />);
    expect(screen.getByText('Match')).toBeInTheDocument();

    rerender(<Badge status="MISMATCH" />);
    expect(screen.getByText('Mismatch')).toBeInTheDocument();

    rerender(<Badge status="UNKNOWN" />);
    expect(screen.getByText('Unknown')).toBeInTheDocument();
  });

  it('renders ScholarshipCard with valid score and reasons', () => {
    const onSelect = vi.fn();
    render(<ScholarshipCard item={mockItemEligible} onSelect={onSelect} />);

    expect(screen.getByText(/Electronic Arts \(EA\) Student Scholarship/)).toBeInTheDocument();
    expect(screen.getByText('95.0 / 100')).toBeInTheDocument();
    expect(screen.getByText(/Direct discipline match for computer science/)).toBeInTheDocument();
    expect(screen.getByText(/UNVERIFIED: Secondary source record/)).toBeInTheDocument();

    const detailBtn = screen.getByText('View Full Evaluation Details');
    fireEvent.click(detailBtn);
    expect(onSelect).toHaveBeenCalledWith(mockItemEligible);
  });

  it('renders null score as "Score unavailable", NOT 0', () => {
    const onSelect = vi.fn();
    render(<ScholarshipCard item={mockItemNullScore} onSelect={onSelect} />);

    expect(screen.getByText('Score unavailable')).toBeInTheDocument();
    expect(screen.queryByText('0 / 100')).not.toBeInTheDocument();
    expect(screen.queryByText('0.0 / 100')).not.toBeInTheDocument();
  });

  it('renders ScholarshipDetailsModal with official application URL when available', () => {
    const onClose = vi.fn();
    render(<ScholarshipDetailsModal item={mockItemEligible} onClose={onClose} />);

    const link = screen.getByText('Visit Official Application Portal');
    expect(link).toBeInTheDocument();
    expect(link.closest('a')).toHaveAttribute('href', 'https://ea.com/scholarships/apply');
    expect(link.closest('a')).toHaveAttribute('target', '_blank');
  });

  it('does NOT create fake link when application URL is missing', () => {
    const onClose = vi.fn();
    render(<ScholarshipDetailsModal item={mockItemNullScore} onClose={onClose} />);

    expect(
      screen.getByText('Official application link not provided by source dataset')
    ).toBeInTheDocument();
    expect(screen.queryByText('Visit Official Application Portal')).not.toBeInTheDocument();
  });

  it('renders EmptyState for error with retry button', () => {
    const onRetry = vi.fn();
    render(
      <EmptyState
        type="error"
        errorMessage="Backend service unavailable"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText('Backend service unavailable')).toBeInTheDocument();
    const retryBtn = screen.getByText('Retry Prediction');
    fireEvent.click(retryBtn);
    expect(onRetry).toHaveBeenCalled();
  });
});
