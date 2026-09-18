export interface StudentProfileFormState {
  // Step 1: Basic
  age: string;
  nationality: string;
  residence_country: string;
  gender: string;

  // Step 2: Education
  education_level: string;
  field_of_study: string;
  custom_field_of_study: string;
  degree: string;
  gpa: string;
  academic_percentage: string;

  // Step 3: Preferences
  preferred_study_country: string;
  study_mode: string;
  funding_preference: string;
  institution_type: string;

  // Step 4: Additional
  family_income: string;
  family_income_currency: string;
  disability_status: boolean;
}

export const INITIAL_FORM_STATE: StudentProfileFormState = {
  age: '20',
  nationality: 'IN',
  residence_country: 'IN',
  gender: 'any',
  education_level: 'undergraduate',
  field_of_study: 'computer_science',
  custom_field_of_study: '',
  degree: 'Bachelor of Science',
  gpa: '3.8',
  academic_percentage: '88',
  preferred_study_country: 'US',
  study_mode: 'full_time',
  funding_preference: 'full',
  institution_type: 'public',
  family_income: '',
  family_income_currency: 'USD',
  disability_status: false,
};

export interface SelectOption {
  value: string;
  label: string;
}

export const EDUCATION_LEVEL_OPTIONS: SelectOption[] = [
  { value: 'undergraduate', label: 'Undergraduate / Bachelor' },
  { value: 'postgraduate', label: 'Postgraduate / Master' },
  { value: 'doctoral', label: 'Doctoral / Ph.D.' },
  { value: 'school', label: 'High School / Secondary' },
  { value: 'diploma', label: 'Diploma / Certificate' },
  { value: 'vocational', label: 'Vocational Training' },
];

export const FIELD_OF_STUDY_OPTIONS: SelectOption[] = [
  { value: 'computer_science', label: 'Computer Science & Software' },
  { value: 'engineering', label: 'Engineering & Technology' },
  { value: 'business', label: 'Business, Finance & Management' },
  { value: 'natural_sciences', label: 'Natural & Physical Sciences' },
  { value: 'medicine', label: 'Medicine & Health Sciences' },
  { value: 'social_sciences', label: 'Social Sciences & Law' },
  { value: 'arts_humanities', label: 'Arts & Humanities' },
  { value: 'other', label: 'Other (Specify below)' },
];

export const STUDY_MODE_OPTIONS: SelectOption[] = [
  { value: 'full_time', label: 'Full-time' },
  { value: 'part_time', label: 'Part-time' },
  { value: 'online', label: 'Online / Remote' },
  { value: 'distance', label: 'Distance Learning' },
];

export const FUNDING_PREFERENCE_OPTIONS: SelectOption[] = [
  { value: 'full', label: 'Full Scholarship (Tuition + Living)' },
  { value: 'partial', label: 'Partial Scholarship' },
  { value: 'tuition_only', label: 'Tuition-only Coverage' },
];

export const COUNTRY_OPTIONS: SelectOption[] = [
  { value: 'US', label: 'United States (USA)' },
  { value: 'UK', label: 'United Kingdom (UK)' },
  { value: 'CA', label: 'Canada' },
  { value: 'IN', label: 'India' },
  { value: 'DE', label: 'Germany' },
  { value: 'AU', label: 'Australia' },
  { value: 'FR', label: 'France' },
  { value: 'SG', label: 'Singapore' },
  { value: 'JP', label: 'Japan' },
  { value: 'other', label: 'Other / Any Country' },
];

export const INSTITUTION_TYPE_OPTIONS: SelectOption[] = [
  { value: 'public', label: 'Public University' },
  { value: 'private', label: 'Private Institution' },
  { value: 'any', label: 'Any Institution Type' },
];

export const CURRENCY_OPTIONS: SelectOption[] = [
  { value: 'USD', label: 'USD ($)' },
  { value: 'INR', label: 'INR (₹)' },
  { value: 'EUR', label: 'EUR (€)' },
  { value: 'GBP', label: 'GBP (£)' },
  { value: 'CAD', label: 'CAD ($)' },
];
