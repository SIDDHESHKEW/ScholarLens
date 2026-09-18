from fastapi.testclient import TestClient

from app.main import app


def test_recommendation_openapi_uses_object_profile_schema() -> None:
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()

    request_schema = schema["components"]["schemas"]["RecommendationRequest"]
    profile_schema = schema["components"]["schemas"]["RawStudentProfile"]
    assert request_schema["type"] == "object"
    assert request_schema["properties"]["student_profile"]["$ref"].endswith("RawStudentProfile")
    assert "field_of_study" in profile_schema["properties"]
    assert "additionalProp1" not in profile_schema["properties"]


def test_recommendations_api_rejects_array_body() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/recommendations",
            json=[{"student_profile": {}, "limit": 2}],
        )
    assert response.status_code == 422


def test_recommendations_api_returns_structured_results() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 20,
                    "education_level": "undergraduate",
                    "field_of_study": "computer_science",
                },
                "limit": 2,
                "include_possibly_eligible": True,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["recommendation_policy_version"] == "v1"
    assert body["recommendations"]
    assert "recommended" not in body["recommendations"][0]
    assert "best" not in body["recommendations"][0]
    assert body["total_candidates"] >= 800
    assert body["recommended_count"] == 2
    assert body["recommendations"][0]["score"] is not None
    assert body["recommendations"][0]["reasons"]


def test_recommendations_api_validates_limit() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/recommendations",
            json={"student_profile": {}, "limit": 0},
        )
    assert response.status_code == 422


def test_recommendations_api_profile_a_live() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 20,
                    "education_level": "undergraduate",
                    "field_of_study": "computer_science",
                },
                "limit": 5,
                "include_possibly_eligible": True,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["total_candidates"] == 811
    assert body["recommended_count"] == 5
    recommendations = body["recommendations"]
    assert len(recommendations) == 5

    for idx, item in enumerate(recommendations, start=1):
        assert item["rank"] == idx
        assert "SYNTHETIC" not in item["title"]
        assert item["score"] is not None
        assert item["score"] > 0
        assert item["eligibility"]["outcome"] in {"ELIGIBLE", "POSSIBLY_ELIGIBLE"}


def test_recommendations_api_profile_b_live() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 22,
                    "education_level": "postgraduate",
                    "field_of_study": "mechanical_engineering",
                },
                "limit": 5,
                "include_possibly_eligible": False,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["total_candidates"] == 811
    assert body["recommended_count"] == 5
    recommendations = body["recommendations"]
    assert len(recommendations) == 5

    # Top items must be real scholarships, not synthetic fixtures
    assert recommendations[0]["scholarship_id"] == 27
    assert "Fulbright" in recommendations[0]["title"]
    assert "SYNTHETIC" not in recommendations[0]["title"]

    for idx, item in enumerate(recommendations, start=1):
        assert item["rank"] == idx
        assert "SYNTHETIC" not in item["title"]
        assert item["eligibility"]["outcome"] == "ELIGIBLE"
        # Scores must be None (not fabricated and not coerced to 0)
        assert item["score"] is None
        assert any("unscored" in w.lower() for w in item["warnings"])


def test_recommendations_api_accepts_funding_preference() -> None:
    """Verifies that funding_preference is supported at the top level and does not 422."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 20,
                    "education_level": "undergraduate",
                    "field_of_study": "computer_science",
                    "funding_preference": "full",
                },
                "limit": 5,
                "include_possibly_eligible": True,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["recommended_count"] == 5
    first = body["recommendations"][0]
    funding_factor = next(
        (f for f in first["matching_factors"] if f["dimension"] == "funding_preference"),
        None,
    )
    assert funding_factor is not None
    assert funding_factor["student_value"] == "full"


def test_recommendations_api_country_matching_with_alias() -> None:
    """Verifies that country matching handles canonical aliases like USA/United States."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 20,
                    "education_level": "undergraduate",
                    "field_of_study": "computer_science",
                    "preferred_study_country": "USA",
                },
                "limit": 5,
                "include_possibly_eligible": True,
            },
        )
    assert response.status_code == 200
    body = response.json()
    for item in body["recommendations"]:
        country_factor = next(
            (f for f in item["matching_factors"] if f["dimension"] == "study_country"),
            None,
        )
        assert country_factor is not None
        if country_factor["scholarship_value"] in {"USA", "United States"}:
            assert country_factor["status"] == "MATCH"


def test_recommendations_api_comprehensive_validation_errors() -> None:
    with TestClient(app) as client:
        # Missing student_profile
        resp = client.post("/api/v1/recommendations", json={"limit": 5})
        assert resp.status_code == 422

        # student_profile as array
        resp = client.post("/api/v1/recommendations", json={"student_profile": []})
        assert resp.status_code == 422

        # student_profile as string
        resp = client.post("/api/v1/recommendations", json={"student_profile": "invalid"})
        assert resp.status_code == 422

        # limit = 0
        resp = client.post(
            "/api/v1/recommendations",
            json={"student_profile": {}, "limit": 0},
        )
        assert resp.status_code == 422

        # limit > 100
        resp = client.post(
            "/api/v1/recommendations",
            json={"student_profile": {}, "limit": 101},
        )
        assert resp.status_code == 422

        # Extra forbidden field in student_profile
        resp = client.post(
            "/api/v1/recommendations",
            json={"student_profile": {"unsupported_random_field": "val"}},
        )
        assert resp.status_code == 422

        # Extra forbidden field at request root
        resp = client.post(
            "/api/v1/recommendations",
            json={"student_profile": {}, "unexpected_extra": "val"},
        )
        assert resp.status_code == 422


def test_recommendations_api_test_matrix_profiles() -> None:
    """Runs the audit test matrix (Test A, B, C, D, E) against the live API."""
    with TestClient(app) as client:
        # TEST A: Undergraduate CS
        resp_a = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 20,
                    "education_level": "undergraduate",
                    "field_of_study": "computer_science",
                },
                "limit": 10,
                "include_possibly_eligible": False,
            },
        )
        assert resp_a.status_code == 200
        body_a = resp_a.json()
        assert body_a["recommended_count"] == 10
        # NOT_ELIGIBLE must never appear
        for r in body_a["recommendations"]:
            assert r["eligibility"]["outcome"] == "ELIGIBLE"

        # TEST B: Postgraduate Mechanical Engineering
        resp_b = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 22,
                    "education_level": "postgraduate",
                    "field_of_study": "mechanical_engineering",
                },
                "limit": 10,
                "include_possibly_eligible": False,
            },
        )
        assert resp_b.status_code == 200
        body_b = resp_b.json()
        assert body_b["recommended_count"] == 10
        for r in body_b["recommendations"]:
            assert r["eligibility"]["outcome"] == "ELIGIBLE"

        # TEST C: Undergraduate CS with supported preferences
        resp_c = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 20,
                    "education_level": "undergraduate",
                    "field_of_study": "computer_science",
                    "preferred_study_country": "USA",
                    "funding_preference": "full",
                },
                "limit": 10,
                "include_possibly_eligible": False,
            },
        )
        assert resp_c.status_code == 200
        body_c = resp_c.json()
        assert body_c["recommended_count"] == 10

        # TEST D: Different discipline (Arts) - must not match CS scholarships
        resp_d = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "education_level": "postgraduate",
                    "field_of_study": "arts",
                },
                "limit": 10,
                "include_possibly_eligible": False,
            },
        )
        assert resp_d.status_code == 200
        body_d = resp_d.json()
        # Top recommendations between A and D must differ
        ids_a = [r["scholarship_id"] for r in body_a["recommendations"][:5]]
        ids_d = [r["scholarship_id"] for r in body_d["recommendations"][:5]]
        assert ids_a != ids_d

        # TEST E: Minimal profile - missing preferences reported honestly as UNKNOWN
        resp_e = client.post(
            "/api/v1/recommendations",
            json={
                "student_profile": {
                    "age": 21,
                    "education_level": "undergraduate",
                    "field_of_study": "computer_science",
                },
                "limit": 10,
                "include_possibly_eligible": False,
            },
        )
        assert resp_e.status_code == 200
        body_e = resp_e.json()
        for r in body_e["recommendations"]:
            unknowns = [f["dimension"] for f in r["matching_factors"] if f["status"] == "UNKNOWN"]
            # Without country, study mode, funding, etc., they must be reported UNKNOWN
            assert "study_country" in unknowns
            assert "funding_preference" in unknowns