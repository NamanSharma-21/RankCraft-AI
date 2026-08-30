"""
Unit & Integration Tests for ATS Features:
Skill Extraction, Normalization, Structured Parsing, ATS Parseability, and Multi-Factor Matchers.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.skill_extractor import skill_extractor
from backend.structured_parser import parse_structured_resume, evaluate_ats_parseability
from backend.matcher import match_job_title, match_experience, match_education

client = TestClient(app)


# -------------------------------------------------------------
# 1. Skill Extraction & Normalization Tests
# -------------------------------------------------------------
def test_skill_extraction_canonicalization():
    text = "Proficient in JS, Py, Postgres, K8s, and fast api. Familiar with ML and NLP models."
    skills = skill_extractor.extract_skills(text)
    
    # Check that canonical forms are returned
    assert "JavaScript" in skills
    assert "Python" in skills
    assert "PostgreSQL" in skills
    assert "Kubernetes" in skills
    assert "FastAPI" in skills
    assert "Machine Learning" in skills
    assert "Natural Language Processing" in skills


def test_jd_skills_required_vs_preferred():
    jd_text = """
    Job Title: Senior Data Scientist
    Requirements:
    - Python, Scikit-Learn, PyTorch, SQL
    Preferred Qualifications:
    - Docker, Kubernetes, AWS, MLOps
    """
    profile = skill_extractor.extract_jd_skills(jd_text)
    
    assert profile["classification_confidence"] == "high"
    assert "Python" in profile["required_skills"]
    assert "Scikit-Learn" in profile["required_skills"]
    assert "PyTorch" in profile["required_skills"]
    assert "Docker" in profile["preferred_skills"]
    assert "Kubernetes" in profile["preferred_skills"]


def test_skill_matching_coverage():
    jd_profile = {
        "all_skills": ["Python", "PyTorch", "Docker", "Kubernetes"],
        "required_skills": ["Python", "PyTorch"],
        "preferred_skills": ["Docker", "Kubernetes"],
        "classification_confidence": "high"
    }
    cand_skills = ["Python", "PyTorch", "Docker"]
    
    match_res = skill_extractor.match_skills(cand_skills, jd_profile)
    assert "Python" in match_res["matched_required"]
    assert "PyTorch" in match_res["matched_required"]
    assert "Docker" in match_res["matched_preferred"]
    assert "Kubernetes" in match_res["missing_preferred"]
    assert match_res["skill_coverage_percentage"] >= 80.0


# -------------------------------------------------------------
# 2. Structured Resume Parsing & ATS Parseability Tests
# -------------------------------------------------------------
def test_structured_parsing_contact_and_timeline():
    sample_text = """
    Dr. Alex Rivera
    Email: alex.rivera@example.com | Phone: (555) 123-4567
    
    Professional Summary:
    Senior AI/ML engineer with 6 years experience architecting deep learning solutions.
    
    Experience:
    Senior AI Engineer at NeuroFlow Systems (2020 - Present)
    ML Engineer at DataCore Inc (2018 - 2020)
    
    Education:
    Ph.D. in Computer Science, Stanford University (2018)
    
    Skills:
    Python, PyTorch, Scikit-Learn, FastAPI, Docker, Kubernetes
    """
    profile = parse_structured_resume(sample_text, "Dr. Alex Rivera")
    
    assert profile["email"] == "alex.rivera@example.com"
    assert profile["phone"] == "(555) 123-4567"
    assert profile["highest_degree"] == "PhD"
    assert "Computer Science" in profile["primary_discipline"]
    assert profile["total_years_experience"] >= 5.0
    assert profile["is_experience_uncertain"] is False
    assert len(profile["skills"]) >= 5

    ats = profile["ats_parseability"]
    assert ats["parseability_score"] >= 85
    assert ats["parseability_grade"] == "High Parseability"


def test_ats_parseability_missing_fields_warning():
    raw_text = "Some random text without clear headings or emails or dates."
    profile = parse_structured_resume(raw_text, "Unknown Candidate")
    ats = profile["ats_parseability"]
    
    assert ats["parseability_score"] < 65
    assert any(c["status"] == "fail" for c in ats["checklist"])


# -------------------------------------------------------------
# 3. Multi-Factor Matchers Tests
# -------------------------------------------------------------
def test_job_title_matching():
    target_title = "Senior AI / Machine Learning Engineer"
    candidate_titles = ["Senior ML Engineer", "Machine Learning Specialist"]
    
    res = match_job_title(target_title, candidate_titles)
    assert res["title_match_score"] >= 0.70
    assert res["status"] == "Direct Role Match"

    unrelated_res = match_job_title(target_title, ["Certified Public Accountant", "Auditor"])
    assert unrelated_res["title_match_score"] < 0.20
    assert unrelated_res["status"] == "Different Domain / Role Discrepancy"


def test_experience_matching():
    jd_text = "Requires 5+ years of experience in ML engineering."
    
    res_meet = match_experience(jd_text, candidate_years=6.0, is_uncertain=False)
    assert res_meet["experience_match_score"] == 1.0
    assert "Meets/Exceeds" in res_meet["status"]

    res_below = match_experience(jd_text, candidate_years=2.0, is_uncertain=False)
    assert res_below["experience_match_score"] == 0.40
    assert "Below Requirement" in res_below["status"]

    res_uncertain = match_experience(jd_text, candidate_years=0.0, is_uncertain=True)
    assert res_uncertain["is_uncertain"] is True
    assert "Uncertain" in res_uncertain["status"]


def test_education_matching():
    jd_text = "Requires Bachelor's degree or higher in Computer Science or related field."
    
    res_phd = match_education(jd_text, highest_degree="PhD", discipline="Computer Science")
    assert res_phd["education_match_score"] == 1.0
    assert "Meets/Exceeds" in res_phd["status"]

    res_unrelated = match_education(jd_text, highest_degree="Bachelor's", discipline="Accounting")
    assert res_unrelated["education_match_score"] == 0.50
    assert "Discipline Mismatch" in res_unrelated["status"]


# -------------------------------------------------------------
# 4. API Endpoints Tests
# -------------------------------------------------------------
def test_skills_taxonomy_api():
    response = client.get("/api/skills-taxonomy")
    assert response.status_code == 200
    data = response.json()
    assert "taxonomy" in data
    assert "Python" in data["taxonomy"]
    assert "JavaScript" in data["taxonomy"]


def test_export_csv_api():
    response = client.get("/api/export-csv?job_filename=job_01_senior_ai_ml_engineer.txt")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    csv_content = response.text
    assert "Rank" in csv_content
    assert "Screening Score" in csv_content
    assert "TF-IDF Cosine Match" in csv_content
    assert "CAND-001" in csv_content
