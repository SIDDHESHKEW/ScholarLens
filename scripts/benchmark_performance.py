import time
import json
import sys
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.recommendations.service import RecommendationService

def benchmark():
    profiles = [
        {"field_of_study": "Computer Science", "education_level": "undergraduate", "study_country": "United States"},
        {"field_of_study": "Mechanical Engineering", "education_level": "postgraduate", "study_country": "Germany"},
        {"field_of_study": "Medicine", "education_level": "undergraduate"},
        {"field_of_study": "Arts and Humanities", "education_level": "postgraduate", "study_country": "United Kingdom"},
        {"field_of_study": "Business", "education_level": "undergraduate", "study_country": "Canada"},
    ]

    latencies = []
    with SessionLocal() as session:
        service = RecommendationService(session, include_synthetic=False)
        # Warmup
        service.generate(profiles[0], limit=10)

        for _ in range(3): # 3 runs of 5 profiles = 15 requests
            for p in profiles:
                start = time.perf_counter()
                resp = service.generate(p, limit=10)
                dur_ms = (time.perf_counter() - start) * 1000
                latencies.append(dur_ms)

    result = {
        "runs_count": len(latencies),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2),
        "mean_ms": round(mean(latencies), 2),
        "median_ms": round(median(latencies), 2),
        "total_candidates_per_request": 811
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    benchmark()
