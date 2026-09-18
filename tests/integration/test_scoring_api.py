from fastapi.testclient import TestClient

from app.main import app


def test_scoring_api_returns_breakdown_without_recommendation_fields() -> None:
    payload = {
        "student": {"age": 20, "education_level": "undergraduate"},
        "scholarship_id": 3,
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/scoring/evaluate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["score_scale"] == "0-100"
    assert body["scoring_policy_version"] == "v1"
    assert "score_breakdown" in body
    assert "recommended" not in body
    assert "best" not in body


def test_ranking_api_excludes_hard_ineligible_records() -> None:
    payload = {
        "student": {"age": 40, "education_level": "undergraduate"},
        "scholarship_ids": [3, 1],
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/scoring/rank", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert 3 in body["excluded_ids"]
    assert all(item["scholarship_id"] != 3 for item in body["results"])