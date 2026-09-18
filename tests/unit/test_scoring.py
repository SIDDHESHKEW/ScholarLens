import pytest

from app.matching.models import MatchFactor, MatchStatus, MatchSummary, SoftMatchResult
from app.scoring.models import ScoringResult
from app.scoring.policy import DEFAULT_POLICY, ScoringPolicy
from app.scoring.service import ScoringService


def match_result(statuses: list[tuple[str, MatchStatus]], eligibility: str = "ELIGIBLE", scholarship_id: int = 1) -> SoftMatchResult:
    factors = [
        MatchFactor(dimension=dimension, status=status, explanation=f"{dimension} explanation")
        for dimension, status in statuses
    ]
    return SoftMatchResult(
        scholarship_id=scholarship_id,
        hard_eligibility_status=eligibility,
        matching_allowed=eligibility != "NOT_ELIGIBLE",
        match_factors=factors,
        matched_dimensions=[item.dimension for item in factors if item.status == MatchStatus.MATCH],
        partially_matched_dimensions=[item.dimension for item in factors if item.status == MatchStatus.PARTIAL_MATCH],
        mismatched_dimensions=[item.dimension for item in factors if item.status == MatchStatus.MISMATCH],
        unknown_dimensions=[item.dimension for item in factors if item.status == MatchStatus.UNKNOWN],
        summary=MatchSummary(
            matches=sum(item.status == MatchStatus.MATCH for item in factors),
            partial_matches=sum(item.status == MatchStatus.PARTIAL_MATCH for item in factors),
            mismatches=sum(item.status == MatchStatus.MISMATCH for item in factors),
            unknown=sum(item.status == MatchStatus.UNKNOWN for item in factors),
        ),
    )


def test_all_matches_score_100() -> None:
    result = ScoringService().score(match_result([(dimension, MatchStatus.MATCH) for dimension in DEFAULT_POLICY.weights]))
    assert result.score == 100.0
    assert result.summary.denominator_weight == 100


def test_partial_mismatch_and_unknown_use_available_denominator() -> None:
    result = ScoringService().score(
        match_result([
            ("field_of_study", MatchStatus.MATCH),
            ("study_country", MatchStatus.PARTIAL_MATCH),
            ("education_level", MatchStatus.MISMATCH),
            ("study_mode", MatchStatus.UNKNOWN),
        ])
    )
    # (30 + 10 + 0) / (30 + 20 + 15) * 100
    assert result.score == 61.54
    assert result.unknown_dimensions == 1
    assert result.score_breakdown[-1].contribution is None


def test_all_unknown_has_no_fabricated_score() -> None:
    result = ScoringService().score(
        match_result([(dimension, MatchStatus.UNKNOWN) for dimension in DEFAULT_POLICY.weights])
    )
    assert result.score is None
    assert result.summary.denominator_weight == 0


def test_not_eligible_is_excluded() -> None:
    result = ScoringService().score(match_result([("field_of_study", MatchStatus.MATCH)], "NOT_ELIGIBLE", 8))
    assert result.ranking_allowed is False
    assert result.score is None
    assert result.score_breakdown == []


def test_possible_eligibility_can_be_scored() -> None:
    result = ScoringService().score(match_result([("field_of_study", MatchStatus.MATCH)], "POSSIBLY_ELIGIBLE", 9))
    assert result.ranking_allowed is True
    assert result.eligibility_status == "POSSIBLY_ELIGIBLE"
    assert result.score == 100.0


def test_breakdown_reconstructs_score() -> None:
    result = ScoringService().score(
        match_result([
            ("field_of_study", MatchStatus.MATCH),
            ("study_country", MatchStatus.PARTIAL_MATCH),
        ])
    )
    numerator = sum(item.contribution or 0 for item in result.score_breakdown)
    denominator = result.summary.denominator_weight
    assert result.score == round(numerator / denominator * 100, 2)


def test_ranking_and_tie_breaking_are_deterministic() -> None:
    service = ScoringService()
    ranked = service.rank([
        match_result([("field_of_study", MatchStatus.MATCH)], scholarship_id=20),
        match_result([("field_of_study", MatchStatus.MATCH)], scholarship_id=10),
        match_result([("field_of_study", MatchStatus.MATCH)], eligibility="NOT_ELIGIBLE", scholarship_id=5),
    ])
    assert [item.scholarship_id for item in ranked.results] == [10, 20]
    assert ranked.excluded_ids == [5]
    assert ranked.excluded_count == 1


def test_invalid_policy_is_rejected() -> None:
    with pytest.raises(ValueError):
        ScoringPolicy(
            version="v-bad",
            weights={"field_of_study": -1},
            contributions=DEFAULT_POLICY.contributions,
        )
