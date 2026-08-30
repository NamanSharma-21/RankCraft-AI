"""
Unit & Integration Tests for SaaS Features:
Authentication, Dashboard, Jobs, Candidates Pipeline, Analytics, and Stage Transitions.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_saas_auth_login():
    res = client.post("/api/auth/login", json={"email": "recruiter@somethingco.com", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "token" in data
    assert data["user"]["email"] == "recruiter@somethingco.com"


def test_saas_auth_signup():
    res = client.post("/api/auth/signup", json={
        "first_name": "Elena",
        "last_name": "Rostova",
        "email": "elena@acme.ai",
        "company": "Acme AI",
        "password": "password123",
        "hiring_focus": "Engineering"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["user"]["company"] == "Acme AI"


def test_saas_dashboard_metrics():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "funnel" in data
    assert "top_candidates" in data
    assert len(data["funnel"]) == 6
    assert data["kpis"]["open_roles"] >= 1


def test_saas_jobs_list_and_create():
    # List jobs
    res = client.get("/api/jobs")
    assert res.status_code == 200
    data = res.json()
    assert len(data["jobs"]) >= 3

    # Create new job
    new_job_payload = {
        "title": "Principal NLP Architect",
        "department": "AI Research",
        "location": "Boston, MA",
        "employment_type": "Full-time",
        "hiring_manager": "Sarah Jenkins",
        "description": "Looking for a Principal NLP Architect with PyTorch, Transformers, LLM fine-tuning, and Scikit-Learn.",
        "required_skills": ["Python", "PyTorch", "NLP"],
        "preferred_skills": ["Transformers", "FastAPI"],
        "experience_req": "7+ Years",
        "education_req": "Master's or Ph.D."
    }
    create_res = client.post("/api/jobs", json=new_job_payload)
    assert create_res.status_code == 200
    created_data = create_res.json()
    assert created_data["status"] == "success"
    assert created_data["job"]["title"] == "Principal NLP Architect"


def test_saas_candidate_stage_update():
    # Update candidate stage to interview
    res = client.patch("/api/candidates/CAND-001/stage", json={"stage": "interview"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["candidate"]["stage"] == "interview"


def test_saas_analytics():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "workspace_status" in data
    assert "summary" in data
    assert "score_distribution" in data
    assert "top_skills_demand" in data
