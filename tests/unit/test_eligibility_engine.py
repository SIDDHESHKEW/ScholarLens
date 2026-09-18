from app.intelligence.eligibility.engine import evaluate_eligibility
from app.intelligence.eligibility.evaluator import evaluate_rule
from app.intelligence.eligibility.result import EligibilityStatus, RuleResult
from app.schemas.common import StudentProfile
from app.schemas.eligibility import EligibilityRule


def rule(field: str, operator: str, value: object, kind: str = "hard") -> dict:
    return {
        "field": field,
        "operator": operator,
        "value": value,
        "requirement_type": kind,
    }


def test_equals_pass_and_fail() -> None:
    profile = StudentProfile(nationality="India")
    assert evaluate_rule(EligibilityRule.model_validate(rule("nationality", "equals", "India")), profile).result == RuleResult.PASS
    assert evaluate_rule(EligibilityRule.model_validate(rule("nationality", "equals", "Nepal")), profile).result == RuleResult.FAIL


def test_in_pass_and_fail() -> None:
    assert evaluate_eligibility(
        {"nationality": "Nepal"}, [rule("nationality", "in", ["India", "Nepal"])]
    ).status == EligibilityStatus.ELIGIBLE
    assert evaluate_eligibility(
        {"nationality": "Bhutan"}, [rule("nationality", "in", ["India", "Nepal"])]
    ).status == EligibilityStatus.NOT_ELIGIBLE


def test_min_and_max_pass_and_fail() -> None:
    result = evaluate_eligibility(
        {"academic_percentage": 85, "age": 20},
        [rule("academic_percentage", "min", 80), rule("age", "max", 25)],
    )
    assert result.status == EligibilityStatus.ELIGIBLE
    assert evaluate_eligibility({"academic_percentage": 72}, [rule("academic_percentage", "min", 80)]).status == EligibilityStatus.NOT_ELIGIBLE
    assert evaluate_eligibility({"age": 30}, [rule("age", "max", 25)]).status == EligibilityStatus.NOT_ELIGIBLE


def test_contains_pass_and_fail() -> None:
    assert evaluate_eligibility(
        {"field_of_study": "Computer Science and Engineering"},
        [rule("field_of_study", "contains", "computer science")],
    ).status == EligibilityStatus.ELIGIBLE
    assert evaluate_eligibility(
        {"field_of_study": "History"}, [rule("field_of_study", "contains", "computer science")]
    ).status == EligibilityStatus.NOT_ELIGIBLE


def test_missing_value_is_unknown_and_possible() -> None:
    result = evaluate_eligibility({"age": 21}, [rule("academic_percentage", "min", 80)])
    assert result.status == EligibilityStatus.POSSIBLY_ELIGIBLE
    assert result.evaluated_rules[0].result == RuleResult.UNKNOWN
    assert "academic_percentage" in result.explanation


def test_hard_failure_overrides_unknown() -> None:
    result = evaluate_eligibility(
        {"nationality": "Nepal", "academic_percentage": None, "age": 21},
        [
            rule("nationality", "equals", "India"),
            rule("academic_percentage", "min", 80),
            rule("age", "max", 25),
        ],
    )
    assert result.status == EligibilityStatus.NOT_ELIGIBLE
    assert [item.field for item in result.failed_rules] == ["nationality"]
    assert [item.field for item in result.unknown_rules] == ["academic_percentage"]


def test_all_hard_rules_pass() -> None:
    result = evaluate_eligibility(
        {"nationality": "India", "academic_percentage": 85, "age": 21},
        [
            rule("nationality", "equals", "India"),
            rule("academic_percentage", "min", 80),
            rule("age", "max", 25),
        ],
    )
    assert result.status == EligibilityStatus.ELIGIBLE
    assert result.explanation == "All known mandatory requirements passed."


def test_soft_rules_do_not_change_eligibility() -> None:
    result = evaluate_eligibility(
        {"nationality": "India"},
        [rule("nationality", "equals", "India"), rule("field_of_study", "equals", "Physics", "soft")],
    )
    assert result.status == EligibilityStatus.ELIGIBLE
    assert not result.failed_rules
    assert result.evaluated_rules[-1].result == RuleResult.UNKNOWN


def test_multiple_hard_failures_are_preserved() -> None:
    result = evaluate_eligibility(
        {"nationality": "Nepal", "age": 30},
        [rule("nationality", "equals", "India"), rule("age", "max", 25)],
    )
    assert result.status == EligibilityStatus.NOT_ELIGIBLE
    assert {item.field for item in result.failed_rules} == {"nationality", "age"}


def test_extra_attributes_are_accessed_without_code_execution() -> None:
    result = evaluate_eligibility(
        {"extra_attributes": {"residency": "India"}},
        [rule("residency", "equals", "India")],
    )
    assert result.status == EligibilityStatus.ELIGIBLE


def test_malformed_and_unsupported_rules_are_structured_unknowns() -> None:
    result = evaluate_eligibility(
        {},
        [
            {"field": "age", "operator": "greater_than", "value": 18, "requirement_type": "hard"},
            {"operator": "min", "value": 80, "requirement_type": "hard"},
        ],
    )
    assert result.status == EligibilityStatus.POSSIBLY_ELIGIBLE
    assert all(item.result == RuleResult.UNKNOWN for item in result.unknown_rules)
    assert all(item.issue for item in result.unknown_rules)


def test_incompatible_types_are_unknown() -> None:
    result = evaluate_eligibility(
        {"academic_percentage": "unknown"}, [rule("academic_percentage", "min", 80)]
    )
    assert result.status == EligibilityStatus.POSSIBLY_ELIGIBLE
    assert result.unknown_rules[0].issue == "incompatible value type"