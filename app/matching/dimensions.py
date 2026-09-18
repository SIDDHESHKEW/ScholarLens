from typing import Any

from app.matching.models import MatchFactor, MatchStatus


def _factor(dimension: str, student: Any, scholarship: Any, status: MatchStatus, explanation: str, verification: str | None = None) -> MatchFactor:
    return MatchFactor(
        dimension=dimension,
        student_value=student,
        scholarship_value=scholarship,
        status=status,
        explanation=explanation,
        data_verification_status=verification,
    )


from app.student.normalizers.country import ALIASES as COUNTRY_ALIASES


def exact_dimension(dimension: str, student: Any, scholarship: Any, label: str, verification: str | None = None) -> MatchFactor:
    if student is None:
        return _factor(dimension, student, scholarship, MatchStatus.UNKNOWN, f"{label} cannot be compared because the student's preference is not specified.", verification)
    if scholarship is None:
        return _factor(dimension, student, scholarship, MatchStatus.UNKNOWN, f"{label} cannot be compared because the scholarship does not specify it.", verification)
    if isinstance(student, str) and isinstance(scholarship, str):
        same = student.casefold() == scholarship.casefold()
    else:
        same = student == scholarship
    status = MatchStatus.MATCH if same else MatchStatus.MISMATCH
    relation = "matches" if same else "does not match"
    return _factor(dimension, student, scholarship, status, f"Student's {label} {relation} the scholarship's {label}.", verification)


def country_dimension(dimension: str, student: Any, scholarship: Any, label: str, verification: str | None = None) -> MatchFactor:
    if student is None:
        return _factor(dimension, student, scholarship, MatchStatus.UNKNOWN, f"{label} cannot be compared because the student's preference is not specified.", verification)
    if scholarship is None:
        return _factor(dimension, student, scholarship, MatchStatus.UNKNOWN, f"{label} cannot be compared because the scholarship does not specify it.", verification)
    if isinstance(student, str) and isinstance(scholarship, str):
        s_student = COUNTRY_ALIASES.get(student.casefold().strip(), student.strip())
        s_scholarship = COUNTRY_ALIASES.get(scholarship.casefold().strip(), scholarship.strip())
        same = s_student.casefold() == s_scholarship.casefold()
    else:
        same = student == scholarship
    status = MatchStatus.MATCH if same else MatchStatus.MISMATCH
    relation = "matches" if same else "does not match"
    return _factor(dimension, student, scholarship, status, f"Student's {label} {relation} the scholarship's {label}.", verification)


import re
from app.intelligence.taxonomy import FieldClassification, classify_scholarship_field

BROAD_TAXONOMY = {
    "engineering": {"computer_science", "information_technology", "artificial_intelligence", "mechanical_engineering", "data_science"},
    "computer_science": {"information_technology", "artificial_intelligence", "data_science"},
}

FIELD_SYNONYMS = {
    "computer_science": {"computer science", "computer & information systems", "computer and information systems", "computing", "cse", "computer science & engineering"},
    "information_technology": {"information technology", "it", "computer & information systems", "computer and information systems"},
    "engineering": {"engineering", "engineering/technology", "technical", "stem (science, technology, engineering, mathematics)"},
    "mechanical_engineering": {"mechanical engineering", "mechanical"},
}


def _split_subfields(text: str) -> list[str]:
    # Split by comma, semicolon, or slash, or ' and '
    parts = re.split(r"[,;/]|\band\b", text, flags=re.IGNORECASE)
    return [p.strip().casefold() for p in parts if p.strip()]


def field_of_study_dimension(student: Any, scholarship: Any, verification: str | None = None) -> MatchFactor:
    if student is None or scholarship is None:
        return exact_dimension("field_of_study", student, scholarship, "field of study", verification)
    student_value = str(student).casefold().strip()
    scholarship_raw = str(scholarship).strip()
    scholarship_value = scholarship_raw.casefold()

    if classify_scholarship_field(scholarship_raw) == FieldClassification.BROAD:
        return _factor(
            "field_of_study",
            student,
            scholarship,
            MatchStatus.MATCH,
            "The scholarship is open to all fields of study (unrestricted), accommodating the student's field of study.",
            verification,
        )

    if student_value == scholarship_value:
        return _factor(
            "field_of_study",
            student,
            scholarship,
            MatchStatus.MATCH,
            "Student's field of study matches the scholarship's field of study.",
            verification,
        )

    if scholarship_value in BROAD_TAXONOMY.get(student_value, set()) or student_value in BROAD_TAXONOMY.get(scholarship_value, set()):
        return _factor(
            "field_of_study",
            student,
            scholarship,
            MatchStatus.PARTIAL_MATCH,
            "The student's field has an explicit broader or adjacent taxonomy relationship with the scholarship field.",
            verification,
        )

    # Check composite/delimited fields in scholarship
    subfields = _split_subfields(scholarship_value)
    has_partial = False
    for sub in subfields:
        if sub == student_value or sub in FIELD_SYNONYMS.get(student_value, set()):
            return _factor(
                "field_of_study",
                student,
                scholarship,
                MatchStatus.MATCH,
                "Student's field of study matches a targeted field in the scholarship.",
                verification,
            )
        if sub in BROAD_TAXONOMY.get(student_value, set()) or student_value in BROAD_TAXONOMY.get(sub, set()):
            has_partial = True

    if has_partial:
        return _factor(
            "field_of_study",
            student,
            scholarship,
            MatchStatus.PARTIAL_MATCH,
            "The student's field has an explicit broader or adjacent taxonomy relationship with a targeted field in the scholarship.",
            verification,
        )

    return _factor(
        "field_of_study",
        student,
        scholarship,
        MatchStatus.MISMATCH,
        "The student's field of study does not match the scholarship field.",
        verification,
    )


def funding_dimension(student: Any, scholarship: Any, verification: str | None = None) -> MatchFactor:
    if student is None or scholarship is None:
        return exact_dimension("funding_preference", student, scholarship, "funding preference", verification)
    student_value = str(student).casefold().replace(" ", "_")
    scholarship_value = str(scholarship).casefold().replace(" ", "_")
    if student_value == scholarship_value:
        return _factor("funding_preference", student, scholarship, MatchStatus.MATCH, "The scholarship's funding type matches the student's funding preference.", verification)
    if student_value == "tuition_and_living" and scholarship_value in {"tuition", "tuition_only"}:
        return _factor("funding_preference", student, scholarship, MatchStatus.PARTIAL_MATCH, "The scholarship covers tuition, while the student prefers tuition and living expenses.", verification)
    return _factor("funding_preference", student, scholarship, MatchStatus.MISMATCH, "The scholarship's funding type does not match the student's funding preference.", verification)