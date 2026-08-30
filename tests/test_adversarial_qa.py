"""
Adversarial QA and Stress-Testing Suite for AI Resume Screening System
Conducts rigorous validation against failure modes, edge cases, data leakage, and API robustness.
"""

import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.preprocessing import preprocess_text, clean_text_pii_and_noise, preserve_tech_terms
from backend.resume_parser import parse_resume, UnsupportedFormatError, FileExtractionError
from backend.ranking import ResumeRanker

client = TestClient(app)


# -------------------------------------------------------------
# Test A, B, C, D, E: Spectrum of Relevance & Determinism
# -------------------------------------------------------------
def test_relevance_spectrum_ordering():
    """
    Scenario A, B, C, D, E: Validates that Highly Relevant > Partially Relevant >
    Weakly Relevant > Irrelevant when ranked against a specific Job Description.
    """
    jd = """
    Senior AI/ML Engineer.
    Requirements: Python, PyTorch, Scikit-Learn, NLP, Transformers, FastAPI, Docker, Kubernetes.
    """
    
    res_high = {
        "candidate_id": "CAND-HIGH",
        "candidate_name": "Senior ML Specialist",
        "raw_text": "Senior ML Engineer with PyTorch, Scikit-Learn, NLP, Transformers, FastAPI, and Docker."
    }
    res_partial = {
        "candidate_id": "CAND-PARTIAL",
        "candidate_name": "Full-Stack Developer",
        "raw_text": "Full-stack developer with Python, FastAPI, Docker, and PostgreSQL databases."
    }
    res_weak = {
        "candidate_id": "CAND-WEAK",
        "candidate_name": "DevOps Engineer",
        "raw_text": "DevOps engineer managing Kubernetes and Docker clusters with shell scripting."
    }
    res_irrelevant = {
        "candidate_id": "CAND-IRRELEVANT",
        "candidate_name": "Accountant",
        "raw_text": "Certified Public Accountant with GAAP auditing, tax preparation, and payroll balance sheets."
    }

    ranker = ResumeRanker()
    ranked = ranker.rank_candidates(jd, [res_high, res_partial, res_weak, res_irrelevant])

    assert len(ranked) == 4
    # Check monotonic rank ordering
    assert ranked[0]["candidate_id"] == "CAND-HIGH"
    assert ranked[1]["candidate_id"] == "CAND-PARTIAL"
    assert ranked[2]["candidate_id"] == "CAND-WEAK"
    assert ranked[3]["candidate_id"] == "CAND-IRRELEVANT"

    # Verify score strictly decreases
    scores = [c["similarity_score"] for c in ranked]
    assert scores[0] > scores[1] > scores[2] > scores[3]
    assert scores[3] < 0.05  # Irrelevant should have negligible score


def test_permutation_invariance():
    """
    Validates that shuffling the input order of resumes does NOT alter
    the resulting similarity scores or assigned rankings.
    """
    jd = "Python FastAPI Docker PostgreSQL Developer"
    res1 = {"candidate_id": "C1", "raw_text": "Python FastAPI Docker PostgreSQL"}
    res2 = {"candidate_id": "C2", "raw_text": "Python SQL"}
    res3 = {"candidate_id": "C3", "raw_text": "Marketing SEO"}

    ranker = ResumeRanker()
    order_a = ranker.rank_candidates(jd, [res1, res2, res3])
    order_b = ranker.rank_candidates(jd, [res3, res1, res2])

    map_a = {c["candidate_id"]: (c["rank"], c["similarity_score"]) for c in order_a}
    map_b = {c["candidate_id"]: (c["rank"], c["similarity_score"]) for c in order_b}

    assert map_a == map_b


# -------------------------------------------------------------
# Test F: Invalid/Unsupported Input Handling
# -------------------------------------------------------------
def test_unsupported_file_extension():
    with pytest.raises(UnsupportedFormatError) as exc_info:
        parse_resume(b"fake data", "resume.exe")
    assert "Unsupported file format" in str(exc_info.value)


def test_empty_or_corrupt_file_handling():
    with pytest.raises(FileExtractionError):
        parse_resume(b"", "empty.txt")


def test_api_unsupported_file_upload():
    files = [
        ("resumes", ("test_image.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png"))
    ]
    data = {"job_description_text": "Python Engineer"}
    response = client.post("/rank", data=data, files=files)
    assert response.status_code == 400
    assert "No valid resumes could be processed" in response.json()["detail"]


# -------------------------------------------------------------
# Test G: Empty or Malformed Job Description
# -------------------------------------------------------------
def test_empty_job_description_handling():
    ranker = ResumeRanker()
    with pytest.raises(ValueError) as exc1:
        ranker.rank_candidates("", [{"raw_text": "Python developer"}])
    assert "Job description cannot be empty" in str(exc1.value)

    with pytest.raises(ValueError) as exc2:
        ranker.rank_candidates("   \n\t  ", [{"raw_text": "Python developer"}])
    assert "Job description cannot be empty" in str(exc2.value)


def test_malformed_noise_only_job_description():
    ranker = ResumeRanker()
    # JD with only punctuation and numbers that gets stripped completely
    with pytest.raises(ValueError) as exc:
        ranker.rank_candidates("!!! @@@ ### $$$ %%% ^^^ &&& 123 456", [{"raw_text": "Python developer"}])
    assert "contains no usable text after preprocessing" in str(exc.value)


def test_api_empty_job_description():
    files = [
        ("resumes", ("cand.txt", io.BytesIO(b"Python developer"), "text/plain"))
    ]
    data = {"job_description_text": "   "}
    response = client.post("/rank", data=data, files=files)
    assert response.status_code == 400
    assert "Please provide a job description" in response.json()["detail"]


# -------------------------------------------------------------
# Test H: API Failure & Error Cases
# -------------------------------------------------------------
def test_api_no_resumes():
    data = {"job_description_text": "Looking for Python engineer"}
    response = client.post("/rank", data=data)
    assert response.status_code == 422  # Unprocessable Entity (missing files field)


def test_api_invalid_json_payload():
    response = client.post("/rank-raw-text", json={"invalid_key": 123})
    assert response.status_code == 422


# -------------------------------------------------------------
# ML Integrity Tests: No Data Leakage, No Hardcoding, Range Checks
# -------------------------------------------------------------
def test_score_boundaries_and_percentages():
    """Validates that all scores are mathematically within [0.0, 1.0] and [0.0, 100.0]."""
    jd = "Machine Learning Python FastAPI"
    resumes = [
        {"candidate_id": "C1", "raw_text": "Machine Learning Python FastAPI"},  # Perfect match
        {"candidate_id": "C2", "raw_text": "Completely unrelated culinary chef baking cakes"},  # Zero overlap
    ]
    ranker = ResumeRanker()
    ranked = ranker.rank_candidates(jd, resumes)

    for c in ranked:
        assert 0.0 <= c["similarity_score"] <= 1.0
        assert 0.0 <= c["score_percentage"] <= 100.0
        assert round(c["similarity_score"] * 100, 2) == c["score_percentage"]


def test_zero_vocabulary_overlap_robustness():
    """Ensures that zero overlap returns score 0.0 without throwing exceptions."""
    jd = "Quantum Physics Astrophysics"
    resumes = [
        {"candidate_id": "C1", "raw_text": "Gardening Horticulture Botanical plants"}
    ]
    ranker = ResumeRanker()
    ranked = ranker.rank_candidates(jd, resumes)
    assert len(ranked) == 1
    assert ranked[0]["similarity_score"] == 0.0
    assert ranked[0]["score_percentage"] == 0.0
    assert ranked[0]["matched_skills"] == []


def test_pii_removal_invariance():
    """
    Validates that changing a candidate's personal contact details (email, phone, name)
    does not artificially alter their technical similarity score.
    """
    jd = "Python FastAPI Docker Developer"
    res_a = "Candidate: Alice Smith | Email: alice@example.com | Phone: 555-0100\nProficient in Python, FastAPI, and Docker."
    res_b = "Candidate: Bob Jones | Email: bjones@techcorp.org | Phone: 555-0999\nProficient in Python, FastAPI, and Docker."

    ranker = ResumeRanker()
    ranked = ranker.rank_candidates(jd, [
        {"candidate_id": "CA", "raw_text": res_a},
        {"candidate_id": "CB", "raw_text": res_b}
    ])

    # Both candidates have identical technical content, differing only in PII
    assert ranked[0]["similarity_score"] == ranked[1]["similarity_score"]
