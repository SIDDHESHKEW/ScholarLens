from collections.abc import Iterable

from app.matching.models import MatchStatus, SoftMatchResult
from app.scoring.models import RankingResult, ScoreBreakdown, ScoringResult, ScoringSummary
from app.scoring.policy import DEFAULT_POLICY, ScoringPolicy


class ScoringService:
    def __init__(self, policy: ScoringPolicy = DEFAULT_POLICY) -> None:
        self.policy = policy

    def score(self, match_result: SoftMatchResult) -> ScoringResult:
        if not match_result.matching_allowed or match_result.hard_eligibility_status == "NOT_ELIGIBLE":
            return self._excluded(match_result)

        breakdown: list[ScoreBreakdown] = []
        denominator = 0.0
        numerator = 0.0
        evaluated = 0
        unknown = 0
        for factor in match_result.match_factors:
            weight = self.policy.weights.get(factor.dimension, 0.0)
            if factor.status == MatchStatus.UNKNOWN:
                unknown += 1
                contribution = None
            else:
                evaluated += 1
                denominator += weight
                contribution = round(weight * self.policy.contributions[factor.status], 2)
                numerator += contribution
            breakdown.append(
                ScoreBreakdown(
                    dimension=factor.dimension,
                    status=factor.status,
                    weight=weight,
                    contribution=contribution,
                    explanation=factor.explanation,
                    data_verification_status=factor.data_verification_status,
                )
            )
        score = None if denominator == 0 else round((numerator / denominator) * 100, 2)
        summary = ScoringSummary(
            evaluated_dimensions=evaluated,
            unknown_dimensions=unknown,
            matches=match_result.summary.matches,
            partial_matches=match_result.summary.partial_matches,
            mismatches=match_result.summary.mismatches,
            denominator_weight=round(denominator, 2),
        )
        return ScoringResult(
            scholarship_id=match_result.scholarship_id,
            eligibility_status=match_result.hard_eligibility_status,
            ranking_allowed=True,
            score=score,
            scoring_policy_version=self.policy.version,
            evaluated_dimensions=evaluated,
            unknown_dimensions=unknown,
            score_breakdown=breakdown,
            summary=summary,
        )

    def _excluded(self, match_result: SoftMatchResult) -> ScoringResult:
        summary = ScoringSummary(
            evaluated_dimensions=0,
            unknown_dimensions=0,
            matches=0,
            partial_matches=0,
            mismatches=0,
            denominator_weight=0,
        )
        return ScoringResult(
            scholarship_id=match_result.scholarship_id,
            eligibility_status=match_result.hard_eligibility_status,
            ranking_allowed=False,
            score=None,
            scoring_policy_version=self.policy.version,
            excluded_reason="Excluded from scoring and ranking because hard eligibility failed.",
            evaluated_dimensions=0,
            unknown_dimensions=0,
            score_breakdown=[],
            summary=summary,
        )

    def rank(self, match_results: Iterable[SoftMatchResult]) -> RankingResult:
        scored = [self.score(result) for result in match_results]
        candidates = [result for result in scored if result.ranking_allowed]
        excluded = [result for result in scored if not result.ranking_allowed]
        priority = {"ELIGIBLE": 0, "POSSIBLY_ELIGIBLE": 1}
        candidates.sort(
            key=lambda result: (
                -(result.score if result.score is not None else -1),
                priority.get(result.eligibility_status, 2),
                -result.evaluated_dimensions,
                result.scholarship_id if result.scholarship_id is not None else 2**31,
            )
        )
        return RankingResult(
            scoring_policy_version=self.policy.version,
            results=candidates,
            excluded_count=len(excluded),
            excluded_ids=[result.scholarship_id for result in excluded if result.scholarship_id is not None],
        )


def score_match(match_result: SoftMatchResult, policy: ScoringPolicy = DEFAULT_POLICY) -> ScoringResult:
    return ScoringService(policy).score(match_result)