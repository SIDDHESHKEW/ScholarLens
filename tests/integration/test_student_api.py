from fastapi.testclient import TestClient

from app.main import app


def test_student_normalization_api_returns_canonical_profile() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/students/normalize",
            json={
                "country": " india ",
                "education_level": "B.Tech",
                "field_of_study": "Computer Science & Engineering",
                "income": "₹ 3,00,000",
                "currency": "INR",
                "disability_status": False,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["country"] == "India"
    assert body["profile"]["education_level"] == "bachelor"
    assert body["profile"]["field_of_study"] == "computer_science"
    assert body["profile"]["annual_family_income"] == 300000
    assert body["normalization"]["disability_status"]["value_state"] == "EXPLICIT_NEGATIVE"


def test_student_normalization_api_reports_unresolved_input() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/students/normalize",
            json={"field_of_study": "Quantum Textile Design"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PARTIALLY_NORMALIZED"
    assert body["profile"]["field_of_study"] is None
    assert body["normalization"]["field_of_study"]["status"] == "UNRESOLVED"