"""
Unit tests for TF-IDF vectorization, multi-factor scoring, and deterministic candidate ranking.
"""

import pytest
from backend.ranking import ResumeRanker


def test_ranking_relative_ordering():
    """
    Verifies that a highly relevant resume ranks above a partially relevant
    and completely irrelevant resume.
    """
    job_desc = """
    Job Title: Senior Machine Learning Engineer
    Requirements: Python, PyTorch, TensorFlow, Scikit-Learn, NLP, Transformers, FastAPI, Docker.
    """

    resumes = [
        {
            "candidate_id": "CAND-001",
            "candidate_name": "ML Specialist",
            "file_name": "ml.pdf",
            "raw_text": "Senior ML Engineer with 5 years in Python, PyTorch, Scikit-Learn, NLP, and FastAPI. B.S. in Computer Science."
        },
        {
            "candidate_id": "CAND-002",
            "candidate_name": "Web Developer",
            "file_name": "web.pdf",
            "raw_text": "Web developer with JavaScript, CSS, HTML, React, and Python scripting. 3 years experience. B.S. in Information Technology."
        },
        {
            "candidate_id": "CAND-003",
            "candidate_name": "Accountant",
            "file_name": "acc.txt",
            "raw_text": "Certified Public Accountant with GAAP auditing, tax filing, and general ledger. 7 years experience. B.A. in Accounting."
        }
    ]

    ranker = ResumeRanker()
    ranked = ranker.rank_candidates(job_desc, resumes)

    assert len(ranked) == 3
    # ML Specialist should be rank 1 with highest screening score
    assert ranked[0]["candidate_id"] == "CAND-001"
    assert ranked[0]["rank"] == 1
    assert ranked[0]["screening_score"] > ranked[1]["screening_score"]
    assert ranked[1]["screening_score"] > ranked[2]["screening_score"]
    assert ranked[2]["candidate_id"] == "CAND-003"


def test_ranking_deterministic_and_tie_breaking():
    job_desc = "Python Backend Engineer with FastAPI and SQL"
    resumes = [
        {"candidate_id": "CAND-B", "candidate_name": "Candidate B", "raw_text": "Python FastAPI Engineer (2020-2023)"},
        {"candidate_id": "CAND-A", "candidate_name": "Candidate A", "raw_text": "Python FastAPI Engineer (2020-2023)"},
    ]

    ranker = ResumeRanker()
    ranked_1 = ranker.rank_candidates(job_desc, resumes)
    ranked_2 = ranker.rank_candidates(job_desc, resumes)

    assert ranked_1 == ranked_2
    # With identical scores, CAND-A should break tie deterministically before CAND-B
    assert ranked_1[0]["candidate_id"] == "CAND-A"
    assert ranked_1[1]["candidate_id"] == "CAND-B"


def test_ranking_empty_job_description():
    ranker = ResumeRanker()
    with pytest.raises(ValueError):
        ranker.rank_candidates("", [{"raw_text": "Some text"}])


def test_ranking_explainability_skills():
    job_desc = """
    Job Title: Cloud Engineer
    Requirements: Docker, Kubernetes, Python, AWS.
    """
    resumes = [
        {
            "candidate_id": "CAND-001",
            "candidate_name": "Cloud Dev",
            "raw_text": "Cloud Engineer with Python, Docker, and AWS cloud experience. 4 years experience."
        }
    ]
    ranker = ResumeRanker()
    ranked = ranker.rank_candidates(job_desc, resumes)

    assert any(s in ranked[0]["matched_skills"] for s in ["Python", "Docker", "AWS"])
    assert "Kubernetes" in ranked[0]["missing_required"]
