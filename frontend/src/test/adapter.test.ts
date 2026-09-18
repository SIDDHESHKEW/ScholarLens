import { describe, it, expect } from 'vitest';
import {
  adaptFormStateToProfile,
  buildRecommendationRequest,
  formatScore,
  formatDimensionName,
} from '../services/adapter';
import { INITIAL_FORM_STATE } from '../types/profile';

describe('Adapter Services', () => {
  it('formats valid score correctly', () => {
    expect(formatScore(95.0)).toBe('95.0 / 100');
    expect(formatScore(86.6666)).toBe('86.7 / 100');
  });

  it('formats null and undefined scores as unavailable, NEVER 0', () => {
    expect(formatScore(null)).toBe('Score unavailable');
    expect(formatScore(undefined)).toBe('Score unavailable');
  });

  it('formats dimension names correctly', () => {
    expect(formatDimensionName('field_of_study')).toBe('Field of Study');
    expect(formatDimensionName('study_country')).toBe('Study Country');
    expect(formatDimensionName('funding_preference')).toBe('Funding Preference');
  });

  it('adapts form state to clean RawStudentProfile without empty junk', () => {
    const profile = adaptFormStateToProfile(INITIAL_FORM_STATE);
    expect(profile.age).toBe(20);
    expect(profile.education_level).toBe('undergraduate');
    expect(profile.field_of_study).toBe('computer_science');
    expect(profile.preferred_study_country).toBe('US');
    expect(profile.gpa).toBe(3.8);
    expect(profile.academic_percentage).toBe(88);
    expect(profile.study_mode).toBe('full_time');
    expect(profile.funding_preference).toBe('full');
    expect(profile.family_income).toBeUndefined();
  });

  it('handles custom field of study when field is other', () => {
    const customForm = {
      ...INITIAL_FORM_STATE,
      field_of_study: 'other',
      custom_field_of_study: 'Robotics & Automation',
    };
    const profile = adaptFormStateToProfile(customForm);
    expect(profile.field_of_study).toBe('Robotics & Automation');
  });

  it('builds complete recommendation request', () => {
    const request = buildRecommendationRequest(INITIAL_FORM_STATE, 10, true);
    expect(request.limit).toBe(10);
    expect(request.include_possibly_eligible).toBe(true);
    expect(request.student_profile.education_level).toBe('undergraduate');
  });
});
