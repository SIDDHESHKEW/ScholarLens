# CSV Column Mapping

The mapping below is based on the observed `data/clean_scholarships.csv` header and values. The original CSV remains unchanged.

| CSV columns | ScholarMatch treatment |
| --- | --- |
| `scholarship_id` | `source_record_id`; preserved as the imported record identifier |
| `scholarship_name`, `provider`, `description` | Direct canonical scholarship fields |
| `official_source_url`, `application_url` | Canonical URL fields and provenance; not verified |
| `source`, `provider_type`, `country_of_provider`, `study_country`, `study_mode`, `field_of_study`, `eligible_nationalities`, `funding_type`, `application_fee`, `scholarship_duration`, `number_of_awards`, `renewable`, `last_verified` | Preserved in `legacy_metadata` and raw payload as source values; not treated as verified facts |
| `currency` | Whitespace/casing-normalized currency |
| `scholarship_amount` | Numeric-only values may become `amount`; ranges/text remain preserved without fabricated numeric values |
| `application_deadline` | ISO dates become `deadline`; rolling, human-readable, or invalid values remain unknown with quality warnings |
| `age_min`, `age_max`, numeric `minimum_percentage_or_gpa`, numeric `family_income_limit` | Deterministic hard rules only when the source value is strictly numeric |
| specific `education_level`, specific `gender_eligibility` | Deterministic equality rules; generic values such as `Any` are not rules |
| `academic_requirement`, `disability_eligibility`, `residency_requirement`, `tuition_coverage`, `living_expense_coverage`, `travel_coverage`, `accommodation_coverage`, `documents_required`, `eligibility_criteria`, `selection_criteria` | Preserved as `eligibility_evidence` with `parsing_status=UNPARSED`; no free-text rule inference |

The inspected dataset contained no columns named like `match_score`, `ranking`, `prediction`, `recommendation`, or `eligibility_status`. If such columns appear in a future extract, they must remain legacy metadata and never feed the Phase 3 engine.

Imported records use `source_type=dataset` and `verification_status=unverified`. A source `last_verified` value is preserved only as source data and does not upgrade ScholarMatch verification.