export type MatchStatus = 'MATCH' | 'PARTIAL_MATCH' | 'MISMATCH' | 'UNKNOWN';

export interface MatchFactor {
  dimension: string;
  student_value?: unknown;
  scholarship_value?: unknown;
  status: MatchStatus;
  explanation: string;
  data_verification_status?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface ScoreBreakdown {
  dimension: string;
  status: MatchStatus;
  weight: number;
  contribution: number | null;
  explanation: string;
  data_verification_status?: string | null;
}

export interface RecommendationEligibility {
  outcome: 'ELIGIBLE' | 'POSSIBLY_ELIGIBLE' | 'NOT_ELIGIBLE';
  unknown_fields: string[];
}

export interface RecommendationVerification {
  status: string;
  freshness: string;
  warnings: string[];
  verified_at?: string | null;
  verifier_method?: string | null;
  notes?: string | null;
}

export interface RecommendationItem {
  rank: number;
  scholarship_id: number;
  title: string;
  provider?: string | null;
  eligibility: RecommendationEligibility;
  score: number | null;
  score_breakdown: ScoreBreakdown[];
  matching_factors: MatchFactor[];
  reasons: string[];
  warnings: string[];
  verification: RecommendationVerification;
  deadline?: string | null;
  application_url?: string | null;
  official_source_url?: string | null;
}

export interface RecommendationExcluded {
  not_eligible_count: number;
  not_eligible_ids: number[];
  quality_blocked_count: number;
  quality_blocked_ids: number[];
}

export interface RecommendationResponse {
  recommendation_policy_version: string;
  scoring_policy_version: string;
  student_profile_status: string;
  total_candidates: number;
  recommended_count: number;
  recommendations: RecommendationItem[];
  excluded: RecommendationExcluded;
}

export interface RawStudentProfile {
  age?: number | null;
  nationality?: string | null;
  residence_country?: string | null;
  country?: string | null;
  education_level?: string | null;
  field_of_study?: string | null;
  preferred_study_country?: string | null;
  study_country?: string | null;
  gpa?: number | null;
  academic_percentage?: number | null;
  study_mode?: string | null;
  funding_preference?: string | null;
  preferred_funding_type?: string | null;
  institution?: string | null;
  institution_type?: string | null;
  degree?: string | null;
  program?: string | null;
  gender?: string | null;
  category?: string | null;
  family_income?: number | null;
  family_income_currency?: string | null;
  disability_status?: boolean | null;
  language?: string | null;
}

export interface RecommendationRequest {
  student_profile: RawStudentProfile;
  limit?: number;
  include_possibly_eligible?: boolean;
}

export interface ScholarshipSourceRead {
  id: number;
  scholarship_id: number;
  source_name: string;
  source_type: string;
  source_url?: string | null;
  verification_status: string;
}

export interface ScholarshipRead {
  id: number;
  name: string;
  provider?: string | null;
  description?: string | null;
  official_source_url?: string | null;
  application_url?: string | null;
  amount?: number | null;
  currency?: string | null;
  deadline?: string | null;
  status?: string;
  requirements?: Record<string, unknown> | null;
  data_quality?: string;
  provenance?: ScholarshipSourceRead[];
}
