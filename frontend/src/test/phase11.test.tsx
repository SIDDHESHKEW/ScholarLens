import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '../components/common/Badge';
import { ScholarshipCard } from '../components/results/ScholarshipCard';
import { ScholarshipDetailsModal } from '../components/results/ScholarshipDetailsModal';
import type { RecommendationItem } from '../types/api';

const mockBaseItem: RecommendationItem = {
  rank: 1,
  scholarship_id: 101,
  title: 'Global Science Leadership Grant',
  provider: 'International Science Foundation',
  eligibility: {
    outcome: 'ELIGIBLE',
    unknown_fields: [],
  },
  score: 85.0,
  score_breakdown: [
    {
      dimension: 'field_of_study',
      status: 'MATCH',
      weight: 30,
      contribution: 30.0,
      explanation: 'Exact field match',
    },
  ],
  matching_factors: [
    {
      dimension: 'field_of_study',
      status: 'MATCH',
      explanation: 'Computer Science matches STEM scope',
    },
  ],
  reasons: ['Field of study matches profile'],
  warnings: [],
  verification: {
    status: 'VERIFIED',
    freshness: 'FRESH',
    warnings: [],
    verified_at: '2026-09-01T12:00:00Z',
    verifier_method: 'controlled_url_fetch',
    notes: 'Identity confirmed against official portal.',
  },
  deadline: '2026-12-31',
  application_url: 'https://example.org/apply',
  official_source_url: 'https://example.org',
};

describe('Phase 11 Verification & Evaluation UI Tests', () => {
  describe('Badge component verification statuses', () => {
    it('renders VERIFIED badge correctly', () => {
      render(<Badge status="VERIFIED" />);
      expect(screen.getByText('Verified')).toBeInTheDocument();
    });

    it('renders PARTIALLY_VERIFIED badge correctly', () => {
      render(<Badge status="PARTIALLY_VERIFIED" />);
      expect(screen.getByText('Partially Verified')).toBeInTheDocument();
    });

    it('renders UNVERIFIED badge correctly', () => {
      render(<Badge status="UNVERIFIED" />);
      expect(screen.getByText('Unverified')).toBeInTheDocument();
    });

    it('renders NEEDS_REVIEW badge correctly', () => {
      render(<Badge status="NEEDS_REVIEW" />);
      expect(screen.getByText('Needs Review')).toBeInTheDocument();
    });

    it('renders SOURCE_UNAVAILABLE badge correctly', () => {
      render(<Badge status="SOURCE_UNAVAILABLE" />);
      expect(screen.getByText('Source Unavailable')).toBeInTheDocument();
    });

    it('renders STALE badge correctly', () => {
      render(<Badge status="STALE" />);
      expect(screen.getByText('Stale')).toBeInTheDocument();
    });

    it('renders CONTRADICTED badge correctly', () => {
      render(<Badge status="CONTRADICTED" />);
      expect(screen.getByText('Contradicted')).toBeInTheDocument();
    });
  });

  describe('ScholarshipCard score and verification behavior', () => {
    it('renders Score unavailable when score is null', () => {
      const unscoredItem: RecommendationItem = {
        ...mockBaseItem,
        score: null,
        warnings: ['Scholarship is unscored because matching criteria could not be evaluated.'],
      };
      render(<ScholarshipCard item={unscoredItem} onSelect={() => {}} />);
      expect(screen.getByText('Score unavailable')).toBeInTheDocument();
      expect(screen.queryByText(/0\.0 \/ 100/)).not.toBeInTheDocument();
    });

    it('renders 0.0 / 100 with explanatory note when score is zero', () => {
      const zeroScoreItem: RecommendationItem = {
        ...mockBaseItem,
        score: 0.0,
      };
      render(<ScholarshipCard item={zeroScoreItem} onSelect={() => {}} />);
      expect(screen.getByText('0.0 / 100')).toBeInTheDocument();
      expect(screen.getByText('No matching factors')).toBeInTheDocument();
    });

    it('does not display unverified warning when item is verified', () => {
      render(<ScholarshipCard item={mockBaseItem} onSelect={() => {}} />);
      expect(screen.getByText('Verified')).toBeInTheDocument();
      expect(screen.queryByText(/not yet been independently verified/i)).not.toBeInTheDocument();
    });

    it('displays unverified warning when item is unverified', () => {
      const unverifiedItem: RecommendationItem = {
        ...mockBaseItem,
        verification: {
          status: 'UNVERIFIED',
          freshness: 'UNKNOWN',
          warnings: ['This scholarship has not yet been independently verified.'],
        },
        warnings: ['This scholarship has not yet been independently verified.'],
      };
      render(<ScholarshipCard item={unverifiedItem} onSelect={() => {}} />);
      expect(screen.getByText('Unverified')).toBeInTheDocument();
      expect(screen.getByText(/This scholarship has not yet been independently verified\./i)).toBeInTheDocument();
    });
  });

  describe('ScholarshipDetailsModal Data & Verification transparency', () => {
    it('renders full Data & Verification transparency section in modal', () => {
      render(<ScholarshipDetailsModal item={mockBaseItem} onClose={() => {}} />);
      expect(screen.getByText('Data & Verification')).toBeInTheDocument();
      expect(screen.getByText('FRESH')).toBeInTheDocument();
      expect(screen.getByText('Identity confirmed against official portal.')).toBeInTheDocument();
      expect(screen.getByText('https://example.org')).toBeInTheDocument();
    });
  });
});
