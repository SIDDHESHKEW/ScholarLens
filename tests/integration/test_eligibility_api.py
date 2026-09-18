from fastapi.testclient import TestClient

from app.main import app


def test_eligibility_api_evaluates_structured_rules() -> None:
    payload = {
        "student": {"nationality": "India", "academic_percentage": 85, "age": 21},
        "rules": [
            {"field": "nationality", "operator": "equals", "value": "India", "requirement_type": "hard"},
            {"field": "academic_percentage", "operator": "min", "value": 80, "requirement_type": "hard"},
            {"field": "age", "operator": "max", "value": 25, "requirement_type": "hard"},
        ],
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/eligibility/evaluate", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "ELIGIBLE"
    assert response.json()["failed_rules"] == []


def test_eligibility_api_keeps_hard_failure_over_unknown() -> None:
    payload = {
        "student": {"nationality": "Nepal", "academic_percentage": None, "age": 21},
        "rules": [
            {"field": "nationality", "operator": "equals", "value": "India", "requirement_type": "hard"},
            {"field": "academic_percentage", "operator": "min", "value": 80, "requirement_type": "hard"},
        ],
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/eligibility/evaluate", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "NOT_ELIGIBLE"
    assert "nationality" in response.json()["explanation"]