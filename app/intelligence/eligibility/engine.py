import logging
from typing import Any, Iterable

from pydantic import ValidationError

from app.schemas.common import StudentProfile
from app.schemas.eligibility import EligibilityRule, RequirementType

from .evaluator import evaluate_rule, invalid_rule_evaluation
from .result import EligibilityEvaluation, EligibilityStatus, RuleResult

logger = logging.getLogger(__name__)


class EligibilityEngine:
    def evaluate(
        self,
        student: StudentProfile | dict[str, Any],
        rules: Iterable[EligibilityRule | dict[str, Any]],
    ) -> EligibilityEvaluation:
        evaluations = []
        for raw_rule in rules:
            try:
                rule = raw_rule if isinstance(raw_rule, EligibilityRule) else EligibilityRule.model_validate(raw_rule)
                evaluations.append(evaluate_rule(rule, student))
            except (ValidationError, ValueError, TypeError) as error:
                logger.warning("eligibility rule validation failed: %s", error)
                evaluations.append(invalid_rule_evaluation(raw_rule, error))

        passed = [item for item in evaluations if item.result == RuleResult.PASS]
        failed = [
            item
            for item in evaluations
            if item.result == RuleResult.FAIL and item.requirement_type == RequirementType.HARD
        ]
        unknown = [
            item
            for item in evaluations
            if item.result == RuleResult.UNKNOWN and item.requirement_type == RequirementType.HARD
        ]
        if failed:
            status = EligibilityStatus.NOT_ELIGIBLE
            explanation = "The student fails at least one mandatory requirement: " + ", ".join(
                item.field for item in failed
            ) + "."
        elif unknown:
            status = EligibilityStatus.POSSIBLY_ELIGIBLE
            explanation = "Eligibility cannot be confirmed because mandatory information is missing, ambiguous, or unresolved: " + ", ".join(
                item.field for item in unknown
            ) + "."
        else:
            status = EligibilityStatus.ELIGIBLE
            explanation = "All known mandatory requirements passed."
        return EligibilityEvaluation(
            status=status,
            evaluated_rules=evaluations,
            passed_rules=passed,
            failed_rules=failed,
            unknown_rules=unknown,
            explanation=explanation,
        )


def evaluate_eligibility(
    student: StudentProfile | dict[str, Any],
    rules: Iterable[EligibilityRule | dict[str, Any]],
) -> EligibilityEvaluation:
    return EligibilityEngine().evaluate(student, rules)