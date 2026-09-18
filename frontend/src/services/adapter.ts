import type {
  RawStudentProfile,
  RecommendationRequest,
} from '../types/api';
import type { StudentProfileFormState } from '../types/profile';

/**
 * Normalizes user form inputs into the exact RawStudentProfile backend transport shape.
 * Omit or set to null empty strings, preserving valid numbers.
 */
export function adaptFormStateToProfile(form: StudentProfileFormState): RawStudentProfile {
  const profile: RawStudentProfile = {};

  const parsedAge = parseInt(form.age, 10);
  if (!isNaN(parsedAge) && parsedAge >= 0) {
    profile.age = parsedAge;
  }

  if (form.nationality.trim()) {
    profile.nationality = form.nationality.trim();
  }

  if (form.residence_country.trim()) {
    profile.residence_country = form.residence_country.trim();
  }

  if (form.education_level.trim()) {
    profile.education_level = form.education_level.trim();
  }

  const selectedField =
    form.field_of_study === 'other' && form.custom_field_of_study.trim()
      ? form.custom_field_of_study.trim()
      : form.field_of_study.trim();

  if (selectedField) {
    profile.field_of_study = selectedField;
  }

  if (form.degree.trim()) {
    profile.degree = form.degree.trim();
  }

  const parsedGpa = parseFloat(form.gpa);
  if (!isNaN(parsedGpa) && parsedGpa >= 0) {
    profile.gpa = parsedGpa;
  }

  const parsedPercentage = parseFloat(form.academic_percentage);
  if (!isNaN(parsedPercentage) && parsedPercentage >= 0 && parsedPercentage <= 100) {
    profile.academic_percentage = parsedPercentage;
  }

  if (form.preferred_study_country.trim()) {
    profile.preferred_study_country = form.preferred_study_country.trim();
  }

  if (form.study_mode.trim()) {
    profile.study_mode = form.study_mode.trim();
  }

  if (form.funding_preference.trim()) {
    profile.funding_preference = form.funding_preference.trim();
  }

  if (form.institution_type.trim() && form.institution_type !== 'any') {
    profile.institution_type = form.institution_type.trim();
  }

  if (form.gender.trim() && form.gender !== 'any') {
    profile.gender = form.gender.trim();
  }

  const parsedIncome = parseFloat(form.family_income);
  if (!isNaN(parsedIncome) && parsedIncome >= 0) {
    profile.family_income = parsedIncome;
    profile.family_income_currency = form.family_income_currency || 'USD';
  }

  if (typeof form.disability_status === 'boolean') {
    profile.disability_status = form.disability_status;
  }

  return profile;
}

/**
 * Builds the complete RecommendationRequest object
 */
export function buildRecommendationRequest(
  form: StudentProfileFormState,
  limit = 5,
  includePossiblyEligible = true
): RecommendationRequest {
  return {
    student_profile: adaptFormStateToProfile(form),
    limit,
    include_possibly_eligible: includePossiblyEligible,
  };
}

/**
 * Formats score display string without converting null to 0
 */
export function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) {
    return 'Score unavailable';
  }
  return `${score.toFixed(1)} / 100`;
}

/**
 * Formats dimension names for human readability
 */
export function formatDimensionName(dimension: string): string {
  const map: Record<string, string> = {
    field_of_study: 'Field of Study',
    study_country: 'Study Country',
    education_level: 'Education Level',
    funding_preference: 'Funding Preference',
    study_mode: 'Study Mode',
    institution_type: 'Institution Type',
    language: 'Language',
  };
  return map[dimension] || dimension.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
