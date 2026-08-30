"""
Integration & Security tests for FastAPI endpoints
"""

import os
import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
DATA_RESUMES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "resumes")


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "TF-IDF" in data["methodology"]


def test_security_headers():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_sample_jobs_endpoint():
    response = client.get("/api/sample-jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert len(data["jobs"]) >= 3


def test_sample_resumes_endpoint():
    response = client.get("/api/sample-resumes")
    assert response.status_code == 200
    data = response.json()
    assert "resumes" in data
    assert data["total"] >= 10


def test_rank_raw_text_api():
    payload = {
        "job_description": "Looking for Python FastAPI developer with PostgreSQL.",
        "resumes": [
            {
                "candidate_id": "CAND-01",
                "candidate_name": "Alice",
                "raw_text": "Experienced Python and FastAPI developer with PostgreSQL and Docker."
            },
            {
                "candidate_id": "CAND-02",
                "candidate_name": "Bob",
                "raw_text": "Certified Public Accountant with general ledger and tax audit."
            }
        ]
    }
    response = client.post("/rank-raw-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    ranked = data["ranked_candidates"]
    assert len(ranked) == 2
    assert ranked[0]["candidate_name"] == "Alice"
    assert ranked[0]["similarity_score"] > ranked[1]["similarity_score"]


def test_rank_sample_data_endpoint():
    response = client.post(
        "/api/rank-sample-data",
        data={"job_filename": "job_01_senior_ai_ml_engineer.txt"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_candidates"] >= 10
    assert data["ranked_candidates"][0]["rank"] == 1


def test_rank_multipart_upload():
    txt_content = b"Python developer with machine learning, scikit-learn, and FastAPI."
    files = [
        ("resumes", ("test_resume.txt", io.BytesIO(txt_content), "text/plain"))
    ]
    data = {
        "job_description_text": "Requires Python and Machine Learning expertise."
    }

    response = client.post("/rank", data=data, files=files)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "success"
    assert len(res_json["ranked_candidates"]) == 1
    assert res_json["ranked_candidates"][0]["similarity_score"] > 0.1


def test_path_traversal_defense():
    # Attempt directory traversal attack on export-csv
    response = client.get("/api/export-csv?job_filename=../../etc/passwd")
    assert response.status_code in [400, 403, 404]

    # Attempt directory traversal attack on sample ranking
    response2 = client.post("/api/rank-sample-data", data={"job_filename": "../../main.py"})
    assert response2.status_code in [400, 403, 404]


def test_spa_fallback_routes():
    res_login = client.get("/login")
    assert res_login.status_code == 200
    assert "RankCraft" in res_login.text

    res_signup = client.get("/signup")
    assert res_signup.status_code == 200

    res_app = client.get("/app/dashboard")
    assert res_app.status_code == 200


def test_invalid_stage_rejection():
    response = client.patch(
        "/api/candidates/CAND-001/stage",
        json={"stage": "invalid_hiring_stage_123"}
    )
    assert response.status_code == 400
