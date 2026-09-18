import re
from typing import Any

from .models import EligibilityEvidenceItem, EvidenceConfidence, EvidenceType


class EvidenceDetector:
    """
    Deterministic, explainable detector for extracting eligibility evidence signals
    from scholarship structured and free-text fields.
    """

    # Incidental patterns where degree mentions refer to faculty/mentors rather than applicants
    INCIDENTAL_PATTERNS = [
        re.compile(r"\b(?:faculty|professors?|supervisors?|advisors?|mentors?|investigators?|staff|members?)\s+(?:who\s+)?(?:hold|have|with)\s+(?:a\s+)?(?:phd|doctorate)s?\b", re.IGNORECASE),
        re.compile(r"\bwork(?:ing)?\s+with\s+(?:faculty|professors?|supervisors?|advisors?|mentors?|investigators?)\s+.*?\b(?:phd|doctorate)s?\b", re.IGNORECASE),
        re.compile(r"\bunder\s+(?:the\s+)?supervision\s+of\s+.*?\b(?:phd|doctorate)s?\b", re.IGNORECASE),
    ]

    # Explicit multi-level target patterns
    MULTI_LEVEL_PATTERNS = [
        (
            re.compile(r"\b(?:open\s+to\s+)?(?:both\s+)?undergraduate\s+and\s+(?:postgraduate|graduate|master'?s?)\b", re.IGNORECASE),
            ["undergraduate", "postgraduate"],
            "Explicit multi-level targeting for undergraduate and postgraduate students.",
        ),
        (
            re.compile(r"\b(?:open\s+to\s+)?(?:both\s+)?(?:master'?s?|postgraduate|graduate)\s+(?:and|or)\s+(?:phd|doctoral)\b", re.IGNORECASE),
            ["postgraduate", "doctoral"],
            "Explicit multi-level targeting for master's/postgraduate and PhD/doctoral students.",
        ),
        (
            re.compile(r"\b(?:open\s+to\s+)?(?:both\s+)?(?:ug\s+and\s+pg|undergraduate\s+and\s+master'?s?)\b", re.IGNORECASE),
            ["undergraduate", "postgraduate"],
            "Explicit multi-level targeting for undergraduate and postgraduate students.",
        ),
    ]

    # High-confidence target and prerequisite patterns
    HIGH_CONFIDENCE_PATTERNS = [
        # Postdoctoral targets & prerequisites
        (
            re.compile(r"\bpostdoc(?:toral)?\s+(?:positions?|fellowships?|scholarships?|opportunit(?:y|ies)|research(?:ers?|)|awards?|programs?|applicants?|candidates?)\b", re.IGNORECASE),
            "postdoctoral",
            "Explicit postdoctoral opportunity or position keyword.",
        ),
        (
            re.compile(r"\b(?:positions?|fellowships?|scholarships?|opportunit(?:y|ies)|awards?)\s+(?:for|in)\s+.*?\bpostdoc(?:toral)?\b", re.IGNORECASE),
            "postdoctoral",
            "Targeted postdoctoral position or fellowship.",
        ),
        (
            re.compile(r"\b(?:for|inviting\s+applicants\s+for)\s+(?:one\s+|a\s+)?postdoc\b", re.IGNORECASE),
            "postdoctoral",
            "Explicit invitation for postdoctoral applicants.",
        ),
        (
            re.compile(r"\bpostdoc\s+opportunity\b", re.IGNORECASE),
            "postdoctoral",
            "Explicit postdoc opportunity target.",
        ),
        (
            re.compile(r"\bapplicants\s+must\s+(?:hold|have|possess)\s+(?:a\s+)?(?:phd|doctorate)\b", re.IGNORECASE),
            "postdoctoral",
            "Prerequisite of holding a PhD/doctorate indicates postdoctoral targeting.",
        ),

        # Doctoral / PhD targets & prerequisites
        (
            re.compile(r"\b(?:phd|doctoral|doctorate)\s+(?:positions?|fellowships?|scholarships?|opportunit(?:y|ies)|candidates?|students?|studies|programs?|admit|degrees?|researchers?)\b", re.IGNORECASE),
            "doctoral",
            "Explicit doctoral or PhD position, fellowship, or scholarship target.",
        ),
        (
            re.compile(r"\b(?:positions?|fellowships?|scholarships?|opportunit(?:y|ies))\s+(?:for|in)\s+.*?\b(?:phd|doctoral)\b", re.IGNORECASE),
            "doctoral",
            "Position or scholarship targeted at doctoral/PhD level.",
        ),
        (
            re.compile(r"\bpursuing\s+(?:a\s+)?(?:phd|doctoral\s+degree)\b", re.IGNORECASE),
            "doctoral",
            "Requires pursuing a PhD or doctoral degree.",
        ),
        (
            re.compile(r"\bapplicants\s+must\s+(?:hold|have|possess)\s+(?:a\s+)?(?:master'?s?|postgraduate)\s+degree\b", re.IGNORECASE),
            "doctoral",
            "Prerequisite of holding a Master's degree indicates doctoral level targeting.",
        ),

        # Postgraduate / Master's targets & prerequisites
        (
            re.compile(r"\b(?:master'?s?|postgraduate|graduate)\s+(?:degrees?|students?|scholarships?|fellowships?|programs?|studies|courses?)\b", re.IGNORECASE),
            "postgraduate",
            "Explicit postgraduate or master's level targeting.",
        ),
        (
            re.compile(r"\bpursuing\s+(?:a\s+)?(?:master'?s?|postgraduate\s+degree)\b", re.IGNORECASE),
            "postgraduate",
            "Requires pursuing a master's or postgraduate degree.",
        ),
        (
            re.compile(r"\bapplicants\s+must\s+(?:hold|have|possess)\s+(?:a\s+)?bachelor'?s?\s+degree\b", re.IGNORECASE),
            "postgraduate",
            "Prerequisite of holding a bachelor's degree indicates postgraduate targeting.",
        ),
        (
            re.compile(r"\bmba\s+(?:scholarships?|fellowships?|students?|programs?|degrees?|awards?)\b", re.IGNORECASE),
            "postgraduate",
            "Explicit MBA level targeting indicates postgraduate level.",
        ),
        (
            re.compile(r"\bpursuing\s+(?:an?\s+)?mba\b", re.IGNORECASE),
            "postgraduate",
            "Requires pursuing an MBA degree indicates postgraduate level.",
        ),

        # Undergraduate targets (must indicate undergraduate program level, not prerequisite of holding a degree)
        (
            re.compile(r"\bundergraduate\s+(?:scholarships?|fellowships?|programs?|awards?|opportunit(?:y|ies)|grants?|studies|courses?)\b", re.IGNORECASE),
            "undergraduate",
            "Explicit undergraduate scholarship or program targeting.",
        ),
        (
            re.compile(r"\bpursuing\s+(?:an?\s+)?(?:undergraduate|bachelor'?s?)\s+degree\b", re.IGNORECASE),
            "undergraduate",
            "Requires actively pursuing an undergraduate or bachelor's degree.",
        ),
        (
            re.compile(r"\b(?:open\s+to|for)\s+undergraduate\s+students?\b", re.IGNORECASE),
            "undergraduate",
            "Explicitly targeted at undergraduate students.",
        ),

        # School targets
        (
            re.compile(r"\b(?:high\s+school|secondary\s+school|class\s+(?:9|10|11|12))\s+(?:students?|scholarships?)\b", re.IGNORECASE),
            "school",
            "Explicit school level targeting.",
        ),
    ]

    def detect_evidence(self, scholarship: Any) -> list[EligibilityEvidenceItem]:
        """
        Inspect all structured and free-text fields in the scholarship record
        and extract eligibility evidence items with provenance and confidence.
        """
        items: list[EligibilityEvidenceItem] = []
        fields = self._extract_fields(scholarship)

        for source_field, text in fields.items():
            if not text or not isinstance(text, str):
                continue
            detected = self._detect_in_text(source_field, text)
            items.extend(detected)

        return items

    def _detect_in_text(self, source_field: str, text: str) -> list[EligibilityEvidenceItem]:
        results: list[EligibilityEvidenceItem] = []

        # First, check for multi-level targets
        multi_matched = False
        for pattern, levels, reason in self.MULTI_LEVEL_PATTERNS:
            match = pattern.search(text)
            if match:
                excerpt = self._clean_excerpt(text, match.start(), match.end())
                for level in levels:
                    results.append(
                        EligibilityEvidenceItem(
                            evidence_type=EvidenceType.EDUCATION_LEVEL_SIGNAL,
                            detected_value=level,
                            confidence=EvidenceConfidence.HIGH,
                            source_field=source_field,
                            text_excerpt=excerpt,
                            reason=reason,
                        )
                    )
                multi_matched = True

        if multi_matched:
            return results

        # Next, check single-level high-confidence patterns
        for pattern, level, reason in self.HIGH_CONFIDENCE_PATTERNS:
            match = pattern.search(text)
            if match:
                # Ensure it is not an incidental reference (e.g. faculty who hold PhDs)
                if self._is_incidental(text, match.start(), match.end()):
                    continue

                excerpt = self._clean_excerpt(text, match.start(), match.end())
                results.append(
                    EligibilityEvidenceItem(
                        evidence_type=EvidenceType.EDUCATION_LEVEL_SIGNAL,
                        detected_value=level,
                        confidence=EvidenceConfidence.HIGH,
                        source_field=source_field,
                        text_excerpt=excerpt,
                        reason=reason,
                    )
                )

        return results

    def _is_incidental(self, text: str, start: int, end: int) -> bool:
        """
        Checks whether the matched region is part of an incidental mention
        (e.g., faculty members who hold PhDs).
        """
        window_start = max(0, start - 100)
        window_end = min(len(text), end + 100)
        snippet = text[window_start:window_end]

        for incidental in self.INCIDENTAL_PATTERNS:
            if incidental.search(snippet):
                return True
        return False

    @staticmethod
    def _clean_excerpt(text: str, start: int, end: int) -> str:
        snippet_start = max(0, start - 20)
        snippet_end = min(len(text), end + 20)
        excerpt = text[snippet_start:snippet_end].strip()
        return " ".join(excerpt.split())

    @staticmethod
    def _extract_fields(scholarship: Any) -> dict[str, str]:
        fields: dict[str, str] = {}
        if isinstance(scholarship, dict):
            if scholarship.get("name"):
                fields["name"] = scholarship["name"]
            if scholarship.get("title"):
                fields["name"] = scholarship["title"]
            if scholarship.get("description"):
                fields["description"] = scholarship["description"]
            evidence = scholarship.get("eligibility_evidence") or {}
            for k, v in evidence.items():
                if isinstance(v, dict) and v.get("raw_text"):
                    fields[f"eligibility_evidence.{k}"] = str(v["raw_text"])
            metadata = scholarship.get("legacy_metadata") or {}
            raw_fields = metadata.get("raw_fields") or {}
            for k in ("eligibility_criteria", "academic_requirement", "selection_criteria", "description"):
                if raw_fields.get(k):
                    fields[f"raw_fields.{k}"] = str(raw_fields[k])
        else:
            if getattr(scholarship, "name", None):
                fields["name"] = scholarship.name
            if getattr(scholarship, "description", None):
                fields["description"] = scholarship.description
            evidence = getattr(scholarship, "eligibility_evidence", None) or {}
            for k, v in evidence.items():
                if isinstance(v, dict) and v.get("raw_text"):
                    fields[f"eligibility_evidence.{k}"] = str(v["raw_text"])
            metadata = getattr(scholarship, "legacy_metadata", None) or {}
            raw_fields = metadata.get("raw_fields") or {}
            for k in ("eligibility_criteria", "academic_requirement", "selection_criteria", "description"):
                if raw_fields.get(k):
                    fields[f"raw_fields.{k}"] = str(raw_fields[k])

        return fields
