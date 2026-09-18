import type { StudentProfileFormState } from '../types/profile';

interface EducationArchetype {
  level: string;
  minAge: number;
  maxAge: number;
  degrees: string[];
}

const EDUCATION_ARCHETYPES: EducationArchetype[] = [
  {
    level: 'undergraduate',
    minAge: 18,
    maxAge: 24,
    degrees: [
      'Bachelor of Science',
      'Bachelor of Technology',
      'Bachelor of Arts',
      'Bachelor of Business Administration',
      'Bachelor of Engineering',
    ],
  },
  {
    level: 'postgraduate',
    minAge: 21,
    maxAge: 32,
    degrees: [
      'Master of Science',
      'Master of Business Administration',
      'Master of Arts',
      'Master of Engineering',
      'Master of Technology',
    ],
  },
  {
    level: 'doctoral',
    minAge: 24,
    maxAge: 40,
    degrees: [
      'Doctor of Philosophy (Ph.D.)',
      'Doctor of Science (D.Sc.)',
      'Doctor of Engineering',
    ],
  },
  {
    level: 'school',
    minAge: 15,
    maxAge: 18,
    degrees: ['High School Diploma', 'Secondary School Certificate'],
  },
  {
    level: 'diploma',
    minAge: 18,
    maxAge: 28,
    degrees: ['Associate Degree', 'Professional Diploma in Technology'],
  },
];

const FIELDS_OF_STUDY = [
  'computer_science',
  'engineering',
  'business',
  'natural_sciences',
  'medicine',
  'social_sciences',
  'arts_humanities',
];

const COUNTRIES = ['US', 'UK', 'CA', 'IN', 'DE', 'AU', 'FR', 'SG', 'JP'];

const STUDY_MODES = ['full_time', 'part_time', 'online'];

const FUNDING_PREFERENCES = ['full', 'partial', 'tuition_only'];

const INSTITUTION_TYPES = ['public', 'private', 'any'];

const GENDERS = ['any', 'female', 'male'];

const CURRENCIES = ['USD', 'INR', 'EUR', 'GBP', 'CAD'];

function pickRandom<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Generates a realistic, schema-valid student profile for testing.
 * Every invocation computes new random attributes with logically consistent education/age/degree combinations.
 */
export function generateRandomProfile(): StudentProfileFormState {
  const archetype = pickRandom(EDUCATION_ARCHETYPES);
  const age = randomInt(archetype.minAge, archetype.maxAge).toString();
  const degree = pickRandom(archetype.degrees);
  const fieldOfStudy = pickRandom(FIELDS_OF_STUDY);

  const nationality = pickRandom(COUNTRIES);
  // 80% chance residence is same as nationality
  const residenceCountry = Math.random() < 0.8 ? nationality : pickRandom(COUNTRIES);

  // Preferred study country
  const preferredStudyCountry = pickRandom(COUNTRIES);

  // Academic performance
  const gpa = (3.0 + Math.random() * 1.0).toFixed(2); // 3.00 - 4.00
  const academicPercentage = randomInt(72, 98).toString();

  const studyMode = pickRandom(STUDY_MODES);
  const fundingPreference = pickRandom(FUNDING_PREFERENCES);
  const institutionType = pickRandom(INSTITUTION_TYPES);
  const gender = pickRandom(GENDERS);

  // Financial info: 50% chance of providing family income
  const hasIncome = Math.random() < 0.5;
  const currency = pickRandom(CURRENCIES);
  let familyIncome = '';
  if (hasIncome) {
    if (currency === 'INR') {
      familyIncome = (randomInt(2, 15) * 100000).toString(); // 200,000 to 1,500,000 INR
    } else {
      familyIncome = (randomInt(25, 120) * 1000).toString(); // 25,000 to 120,000 USD/EUR/GBP/CAD
    }
  }

  // Disability status (10% true, 90% false)
  const disabilityStatus = Math.random() < 0.1;

  return {
    age,
    nationality,
    residence_country: residenceCountry,
    gender,
    education_level: archetype.level,
    field_of_study: fieldOfStudy,
    custom_field_of_study: '',
    degree,
    gpa,
    academic_percentage: academicPercentage,
    preferred_study_country: preferredStudyCountry,
    study_mode: studyMode,
    funding_preference: fundingPreference,
    institution_type: institutionType,
    family_income: familyIncome,
    family_income_currency: currency,
    disability_status: disabilityStatus,
  };
}
