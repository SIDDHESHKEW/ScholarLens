from fastapi.testclient import TestClient

from app.main import app


def test_matching_api_returns_factors_without_score() -> None:
    payload = {
        "student": {
            "field_of_study": "computer_science",
            "preferred_study_country": "Germany",
            "extra_attributes": {"preferred_funding_type": "tuition_and_living"},
        },
        "scholarship_id": 3,
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/matching/evaluate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["matching_allowed"] is True
    assert "summary" in body
    assert "score" not in body
    assert "match_score" not in body


def test_matching_api_returns_404_for_unknown_scholarship() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/matching/evaluate",
            json={"student": {}, "scholarship_id": 999999},
        )
    assert response.status_code == 404