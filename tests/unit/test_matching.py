from app.matching.service import evaluate_soft_match
from app.matching.models import MatchStatus


def scholarship(**metadata):
    return {"id": 7, "requirements": [], "legacy_metadata": metadata}


def test_exact_field_country_education_and_mode_matches() -> None:
    result = evaluate_soft_match(
        {
            "field_of_study": "computer_science",
            "preferred_study_country": "Germany",
            "education_level": "undergraduate",
            "study_mode": "online",
            "extra_attributes": {"preferred_funding_type": "tuition"},
        },
        scholarship(
            field_of_study="computer_science",
            study_country="Germany",
            education_level="undergraduate",
            study_mode="online",
            funding_type="tuition",
        ),
    )
    assert result.matching_allowed is True
    assert result.summary.matches == 5
    assert result.summary.mismatches == 0


def test_field_taxonomy_partial_and_country_mismatch() -> None:
    result = evaluate_soft_match(
        {"field_of_study": "computer_science", "preferred_study_country": "Germany"},
        scholarship(field_of_study="engineering", study_country="France"),
    )
    factors = {factor.dimension: factor for factor in result.match_factors}
    assert factors["field_of_study"].status == MatchStatus.PARTIAL_MATCH
    assert factors["study_country"].status == MatchStatus.MISMATCH


def test_funding_partial_match() -> None:
    result = evaluate_soft_match(
        {"extra_attributes": {"preferred_funding_type": "tuition_and_living"}},
        scholarship(funding_type="tuition"),
    )
    assert result.match_factors[4].status == MatchStatus.PARTIAL_MATCH


def test_missing_values_are_unknown_not_mismatch() -> None:
    result = evaluate_soft_match({"preferred_study_country": "Germany"}, scholarship())
    factors = {factor.dimension: factor for factor in result.match_factors}
    assert factors["study_country"].status == MatchStatus.UNKNOWN
    assert factors["field_of_study"].status == MatchStatus.UNKNOWN


def test_not_eligible_is_excluded_before_soft_matching() -> None:
    result = evaluate_soft_match(
        {"age": 40, "field_of_study": "computer_science"},
        {"id": 9, "requirements": [{"field": "age", "operator": "max", "value": 25, "requirement_type": "hard"}], "legacy_metadata": {"field_of_study": "computer_science"}},
    )
    assert result.hard_eligibility_status == "NOT_ELIGIBLE"
    assert result.matching_allowed is False
    assert result.match_factors == []
    assert result.summary.matches == 0


def test_possible_eligibility_preserves_uncertainty_and_matching() -> None:
    result = evaluate_soft_match(
        {"field_of_study": "computer_science"},
        {"id": 10, "requirements": [{"field": "academic_percentage", "operator": "min", "value": 80, "requirement_type": "hard"}], "legacy_metadata": {"field_of_study": "computer_science"}},
    )
    assert result.hard_eligibility_status == "POSSIBLY_ELIGIBLE"
    assert result.matching_allowed is True
    assert result.match_factors[0].status == MatchStatus.MATCH


def test_unverified_data_is_annotated_without_becoming_verified() -> None:
    result = evaluate_soft_match(
        {"field_of_study": "computer_science"},
        scholarship(field_of_study="computer_science"),
    )
    assert all(factor.data_verification_status is None for factor in result.match_factors)


def test_matching_is_deterministic_and_has_no_score() -> None:
    student = {"preferred_study_country": "Germany"}
    target = scholarship(study_country="France")
    first = evaluate_soft_match(student, target).model_dump()
    second = evaluate_soft_match(student, target).model_dump()
    assert first == second
    assert "score" not in first
    assert "match_score" not in first