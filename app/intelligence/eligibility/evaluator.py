from enum import Enum
from typing import Any

from pydantic import ValidationError

from app.schemas.common import StudentProfile
from app.schemas.eligibility import EligibilityRule, RequirementType, RuleOperator

from . import operators
from .result import RuleEvaluation, RuleResult


def _profile_values(profile: StudentProfile | dict[str, Any]) -> dict[str, Any]:
    if isinstance(profile, StudentProfile):
        values = profile.model_dump()
    else:
        values = dict(profile)
    extra_attributes = values.get("extra_attributes")
    if isinstance(extra_attributes, dict):
        values = {**values, **extra_attributes}
    return values


def _display_value(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


def _actual_value(profile: StudentProfile | dict[str, Any], field: str) -> Any:
    return _display_value(_profile_values(profile).get(field))


def evaluate_rule(rule: EligibilityRule, profile: StudentProfile | dict[str, Any]) -> RuleEvaluation:
    actual = _actual_value(profile, rule.field)
    required = _display_value(rule.value)
    base = {
        "field": rule.field,
        "operator": rule.operator,
        "required_value": required,
        "actual_value": actual,
        "requirement_type": rule.requirement_type,
        "source_reference": rule.source_reference,
    }
    if rule.operator == RuleOperator.UNKNOWN:
        return RuleEvaluation(
            **base,
            result=RuleResult.UNKNOWN,
            reason="The rule operator is unresolved.",
            issue="unsupported or unresolved operator",
        )
    if required is None and rule.operator not in (RuleOperator.NOT_EQUALS,):
        return RuleEvaluation(
            **base,
            result=RuleResult.UNKNOWN,
            reason="The requirement value is missing or unresolved.",
            issue="missing required value",
        )
    if actual is None:
        return RuleEvaluation(
            **base,
            result=RuleResult.UNKNOWN,
            reason=f"The student's {rule.field} information is missing or unresolved.",
        )

    comparison = {
        RuleOperator.EQUALS: lambda: operators.equals(actual, required),
        RuleOperator.NOT_EQUALS: lambda: operators.not_equals(actual, required),
        RuleOperator.IN: lambda: operators.membership(actual, required),
        RuleOperator.NOT_IN: lambda: operators.membership(actual, required, invert=True),
        RuleOperator.MIN: lambda: operators.minimum(actual, required),
        RuleOperator.MAX: lambda: operators.maximum(actual, required),
        RuleOperator.CONTAINS: lambda: operators.contains(actual, required),
    }.get(rule.operator)
    if comparison is None:
        return RuleEvaluation(
            **base,
            result=RuleResult.UNKNOWN,
            reason="The rule operator is not supported.",
            issue="unsupported operator",
        )

    result = comparison()
    if result is None:
        return RuleEvaluation(
            **base,
            result=RuleResult.UNKNOWN,
            reason="The student value and requirement have incompatible types.",
            issue="incompatible value type",
        )
    passed = result
    if passed:
        reason = f"The student's {rule.field} satisfies the requirement."
    elif rule.operator == RuleOperator.MIN:
        reason = f"The student's {rule.field} is below the required minimum."
    elif rule.operator == RuleOperator.MAX:
        reason = f"The student's {rule.field} exceeds the permitted maximum."
    else:
        reason = f"The student's {rule.field} does not satisfy the requirement."
    return RuleEvaluation(**base, result=RuleResult.PASS if passed else RuleResult.FAIL, reason=reason)


def invalid_rule_evaluation(raw_rule: Any, error: ValidationError | ValueError) -> RuleEvaluation:
    raw = raw_rule if isinstance(raw_rule, dict) else {}
    return RuleEvaluation(
        field=str(raw.get("field") or "<invalid rule>"),
        operator=RuleOperator.UNKNOWN,
        required_value=raw.get("value"),
        actual_value=None,
        requirement_type=RequirementType.HARD,
        result=RuleResult.UNKNOWN,
        reason="The eligibility rule is malformed and could not be evaluated.",
        source_reference=raw.get("source_reference"),
        issue=str(error),
    )