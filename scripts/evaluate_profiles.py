import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.recommendations.service import RecommendationService

def evaluate_all():
    profiles = {
        "Profile A (Undergrad CS USA Full-time Full)": {
            "age": 20,
            "education_level": "undergraduate",
            "field_of_study": "Computer Science",
            "preferred_study_country": "United States",
            "study_country": "United States",
            "study_mode": "full-time",
            "funding_preference": "full",
        },
        "Profile B (Postgrad Mech Eng Germany Full-time Full)": {
            "age": 22,
            "education_level": "postgraduate",
            "field_of_study": "Mechanical Engineering",
            "preferred_study_country": "Germany",
            "study_country": "Germany",
            "study_mode": "full-time",
            "funding_preference": "full",
        },
        "Profile C (Undergrad CS Minimal)": {
            "age": 20,
            "education_level": "undergraduate",
            "field_of_study": "Computer Science",
        },
        "Profile D (Postgrad Arts/Humanities UK Full-time Full)": {
            "age": 24,
            "education_level": "postgraduate",
            "field_of_study": "Arts and Humanities",
            "preferred_study_country": "United Kingdom",
            "study_country": "United Kingdom",
            "study_mode": "full-time",
            "funding_preference": "full",
        },
        "Profile E (Undergrad Eng India Full-time)": {
            "age": 19,
            "education_level": "undergraduate",
            "field_of_study": "Engineering",
            "preferred_study_country": "India",
            "study_country": "India",
            "study_mode": "full-time",
        },
        "Profile F (Undergrad vs Doctoral Contradiction)": {
            "age": 19,
            "education_level": "undergraduate",
            "field_of_study": "Physics",
        },
    }

    report = {}
    with SessionLocal() as session:
        service = RecommendationService(session, include_synthetic=False)
        for name, profile in profiles.items():
            resp = service.generate(profile, limit=5)
            recs_summary = []
            for r in resp.recommendations:
                recs_summary.append({
                    "rank": r.rank,
                    "id": r.scholarship_id,
                    "title": r.title,
                    "outcome": r.eligibility.outcome,
                    "score": r.score,
                    "verification_status": r.verification.status,
                    "warnings": r.warnings,
                    "reasons": r.reasons[:2] if r.reasons else [],
                })
            report[name] = {
                "total_candidates": resp.total_candidates,
                "recommended_count": resp.recommended_count,
                "not_eligible_count": resp.excluded.not_eligible_count,
                "quality_blocked_count": resp.excluded.quality_blocked_count,
                "recommendations": recs_summary,
            }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    evaluate_all()
