"""
FastAPI Backend Application - SaaS Edition
RankCraft AI: Intelligent Recruiting Workspace & Multi-Factor Candidate Screening
"""

import os
import io
import csv
import re
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, Response, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.resume_parser import parse_resume, FileExtractionError, UnsupportedFormatError
from backend.ranking import ResumeRanker
from backend.skill_extractor import skill_extractor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DATA_DIR = os.path.join(BASE_DIR, "data")
RESUMES_DIR = os.path.join(DATA_DIR, "resumes")
JD_DIR = os.path.join(DATA_DIR, "job_descriptions")

# Security Constraints
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB per file
MAX_JD_SIZE_BYTES = 5 * 1024 * 1024     # 5 MB for Job Description
MAX_RESUMES_BATCH_COUNT = 50            # Max 50 resumes per screening run
MAX_TEXT_INPUT_LENGTH = 150_000         # Max 150,000 chars per raw text string

app = FastAPI(
    title="RankCraft AI API",
    description="Intelligent Recruiting Workspace & Multi-Factor Candidate Screening Engine combining TF-IDF Cosine Similarity with structured parsing and pipeline management.",
    version="3.0.0"
)

# Configurable CORS
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if raw_origins == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Adds standard defensive HTTP headers to every API response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# -------------------------------------------------------------
# Security & Sanitization Helpers
# -------------------------------------------------------------
def _sanitize_filename(raw_filename: str) -> str:
    """Sanitizes user-supplied filenames to prevent path traversal and shell injection."""
    if not raw_filename:
        return "unnamed_resume.txt"
    base = os.path.basename(raw_filename).strip()
    clean = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', base)
    return clean[:120] if clean else "resume.txt"


def _safe_resolve_job_file(job_filename: str) -> str:
    """
    Safely resolves a job description filename within JD_DIR,
    strictly preventing directory traversal.
    """
    safe_name = os.path.basename(job_filename).strip()
    if not safe_name or not safe_name.endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job description filename. Must be a .txt file."
        )
    target_path = os.path.abspath(os.path.join(JD_DIR, safe_name))
    jd_dir_abs = os.path.abspath(JD_DIR)
    if not target_path.startswith(jd_dir_abs):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to path outside job descriptions directory is forbidden."
        )
    if not os.path.exists(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description file '{safe_name}' not found."
        )
    return target_path


# -------------------------------------------------------------
# In-Memory SaaS State Store (Seeded with Realistic Demo Data)
# -------------------------------------------------------------
class WorkspaceStore:
    def __init__(self):
        self.users = {
            "recruiter@somethingco.com": {
                "id": "usr_001",
                "name": "Sarah Jenkins",
                "email": "recruiter@somethingco.com",
                "role": "Lead Technical Recruiter",
                "company": "SomethingCo",
                "workspace": "SomethingCo Talent",
                "avatar_initials": "SJ",
                "token": "demo_token_sj_2026"
            }
        }
        self.jobs = [
            {
                "id": "job_01",
                "title": "Senior AI / Machine Learning Engineer",
                "department": "AI & Engineering",
                "location": "San Francisco, CA (Hybrid)",
                "employment_type": "Full-time",
                "status": "Open",
                "hiring_manager": "Dr. Marcus Vance",
                "filename": "job_01_senior_ai_ml_engineer.txt",
                "created_at": "2026-08-15",
                "candidates_count": 12,
                "screened_count": 12,
                "required_skills": ["Python", "Machine Learning", "PyTorch", "Scikit-Learn", "FastAPI", "Docker"],
                "preferred_skills": ["Kubernetes", "Transformers", "MLOps", "CI/CD"],
                "experience_req": "5+ Years",
                "education_req": "Bachelor's or higher in CS/AI"
            },
            {
                "id": "job_02",
                "title": "Full-Stack Python Developer",
                "department": "Product Engineering",
                "location": "New York, NY (Remote)",
                "employment_type": "Full-time",
                "status": "Open",
                "hiring_manager": "Elena Rostova",
                "filename": "job_02_fullstack_python_developer.txt",
                "created_at": "2026-08-20",
                "candidates_count": 8,
                "screened_count": 8,
                "required_skills": ["Python", "FastAPI", "Django", "PostgreSQL", "HTML5", "CSS3", "JavaScript"],
                "preferred_skills": ["Docker", "AWS", "CI/CD", "Git"],
                "experience_req": "3+ Years",
                "education_req": "Bachelor's in CS/Engineering"
            },
            {
                "id": "job_03",
                "title": "Data Analyst & Business Intelligence Specialist",
                "department": "Data & Analytics",
                "location": "Austin, TX (Remote)",
                "employment_type": "Full-time",
                "status": "Open",
                "hiring_manager": "David Kim",
                "filename": "job_03_data_analyst.txt",
                "created_at": "2026-08-22",
                "candidates_count": 6,
                "screened_count": 6,
                "required_skills": ["SQL", "Python", "Pandas", "NumPy", "Tableau", "Power BI"],
                "preferred_skills": ["ETL", "Data Warehousing", "Data Visualization"],
                "experience_req": "3+ Years",
                "education_req": "Bachelor's in Analytics/Math/CS"
            },
            {
                "id": "job_04",
                "title": "Lead Cloud Infrastructure Engineer",
                "department": "DevOps & Cloud",
                "location": "Seattle, WA (Remote)",
                "employment_type": "Full-time",
                "status": "Draft",
                "hiring_manager": "Lucas Meyer",
                "filename": "",
                "created_at": "2026-08-28",
                "candidates_count": 0,
                "screened_count": 0,
                "required_skills": ["Kubernetes", "Docker", "AWS", "CI/CD", "Linux"],
                "preferred_skills": ["Terraform", "Python", "Prometheus"],
                "experience_req": "6+ Years",
                "education_req": "Bachelor's in CS or equivalent"
            }
        ]
        self.candidates_pipeline = [
            {"id": "CAND-001", "name": "Dr. Alex Rivera", "role": "Senior AI/ML Engineer", "job_id": "job_01", "stage": "interview", "score": 78.3, "tfidf": 30.1, "applied_date": "2026-08-25", "email": "alex.rivera@neuroflow.ai", "phone": "(555) 123-4567"},
            {"id": "CAND-002", "name": "Sarah Chen", "role": "NLP Data Scientist", "job_id": "job_01", "stage": "shortlisted", "score": 71.5, "tfidf": 22.8, "applied_date": "2026-08-25", "email": "sarah.chen@nlp-labs.org", "phone": "(555) 234-5678"},
            {"id": "CAND-003", "name": "Marcus Vance", "role": "Full-Stack Python Dev", "job_id": "job_02", "stage": "offer", "score": 84.2, "tfidf": 34.5, "applied_date": "2026-08-24", "email": "marcus.vance@cloudstack.io", "phone": "(555) 345-6789"},
            {"id": "CAND-004", "name": "Elena Rostova", "role": "Backend Python Engineer", "job_id": "job_02", "stage": "interview", "score": 76.8, "tfidf": 27.4, "applied_date": "2026-08-24", "email": "elena.rostova@apihub.dev", "phone": "(555) 456-7890"},
            {"id": "CAND-005", "name": "David Kim", "role": "Senior Data Analyst", "job_id": "job_03", "stage": "shortlisted", "score": 79.4, "tfidf": 28.9, "applied_date": "2026-08-26", "email": "david.kim@bi-analytics.com", "phone": "(555) 567-8901"},
            {"id": "CAND-006", "name": "Priya Patel", "role": "Junior Data Scientist", "job_id": "job_01", "stage": "screening", "score": 58.2, "tfidf": 16.4, "applied_date": "2026-08-26", "email": "priya.patel@datascience.net", "phone": "(555) 678-9012"},
            {"id": "CAND-007", "name": "Lucas Meyer", "role": "DevOps & Cloud Engineer", "job_id": "job_01", "stage": "screening", "score": 51.0, "tfidf": 14.2, "applied_date": "2026-08-27", "email": "lucas.meyer@devops-cloud.io", "phone": "(555) 789-0123"},
            {"id": "CAND-008", "name": "Chloe Martin", "role": "Frontend Developer", "job_id": "job_02", "stage": "applied", "score": 45.0, "tfidf": 11.0, "applied_date": "2026-08-28", "email": "chloe.martin@uicrafters.com", "phone": "(555) 890-1234"},
            {"id": "CAND-009", "name": "James Wilson", "role": "Digital Marketing Specialist", "job_id": "job_03", "stage": "applied", "score": 24.5, "tfidf": 4.1, "applied_date": "2026-08-28", "email": "james.wilson@growthseomedia.com", "phone": "(555) 901-2345"},
            {"id": "CAND-010", "name": "Olivia Taylor", "role": "Certified Public Accountant", "job_id": "job_01", "stage": "rejected", "score": 12.0, "tfidf": 0.0, "applied_date": "2026-08-28", "email": "olivia.taylor@apexaccounting.com", "phone": "(555) 012-3456"},
            {"id": "CAND-011", "name": "Ethan Davis", "role": "Senior Technical Writer", "job_id": "job_01", "stage": "rejected", "score": 18.2, "tfidf": 2.5, "applied_date": "2026-08-29", "email": "ethan.davis@techdocspro.org", "phone": "(555) 123-7890"},
            {"id": "CAND-012", "name": "Sophia Martinez", "role": "Database Administrator", "job_id": "job_02", "stage": "applied", "score": 48.0, "tfidf": 13.5, "applied_date": "2026-08-29", "email": "sophia.martinez@enterprise-db.net", "phone": "(555) 234-8901"}
        ]
        self.activity_log = [
            {"id": "act_1", "action": "Candidate Moved", "description": "Dr. Alex Rivera moved to Interview stage", "time": "10 minutes ago", "user": "Sarah Jenkins"},
            {"id": "act_2", "action": "Screening Completed", "description": "AI Screening completed for Senior AI/ML Engineer (12 candidates)", "time": "1 hour ago", "user": "System AI"},
            {"id": "act_3", "action": "Candidate Shortlisted", "description": "Sarah Chen shortlisted for Senior AI/ML Engineer", "time": "3 hours ago", "user": "Sarah Jenkins"},
            {"id": "act_4", "action": "New Job Created", "description": "Lead Cloud Infrastructure Engineer drafted", "time": "1 day ago", "user": "Sarah Jenkins"}
        ]

store = WorkspaceStore()


# -------------------------------------------------------------
# Pydantic Schemas for API
# -------------------------------------------------------------
class LoginRequest(BaseModel):
    email: str = Field(..., max_length=120)
    password: str = Field(..., max_length=120)


class SignupRequest(BaseModel):
    first_name: str = Field(..., max_length=60)
    last_name: str = Field(..., max_length=60)
    email: str = Field(..., max_length=120)
    company: str = Field(..., max_length=120)
    password: str = Field(..., max_length=120)
    hiring_focus: Optional[str] = Field("Engineering", max_length=60)


class CreateJobRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    department: str = Field(..., min_length=2, max_length=120)
    location: str = Field(..., min_length=2, max_length=120)
    employment_type: str = Field("Full-time", max_length=60)
    hiring_manager: str = Field("Sarah Jenkins", max_length=100)
    description: str = Field(..., min_length=10, max_length=MAX_TEXT_INPUT_LENGTH)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_req: str = Field("3+ Years", max_length=60)
    education_req: str = Field("Bachelor's Degree", max_length=100)


class StageUpdateRequest(BaseModel):
    stage: str = Field(..., max_length=30)


class ResumeTextInput(BaseModel):
    candidate_id: Optional[str] = Field(None, max_length=60, description="Optional candidate identifier")
    candidate_name: Optional[str] = Field(None, max_length=100, description="Candidate name")
    file_name: Optional[str] = Field("resume.txt", max_length=120, description="Resume document title")
    raw_text: str = Field(..., min_length=1, max_length=MAX_TEXT_INPUT_LENGTH, description="Raw text of resume")


class RankJsonRequest(BaseModel):
    job_description: str = Field(..., min_length=5, max_length=MAX_TEXT_INPUT_LENGTH, description="Text of job description")
    resumes: List[ResumeTextInput] = Field(..., min_length=1, max_length=MAX_RESUMES_BATCH_COUNT, description="List of resumes to evaluate")


# -------------------------------------------------------------
# System & SaaS Authentication Endpoints
# -------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    """Returns operational status, version, and methodology."""
    return {
        "status": "healthy",
        "service": "RankCraft AI Recruiting Workspace API",
        "version": "3.0.0",
        "methodology": "TF-IDF + Cosine Similarity",
        "primary_ml_methodology": "TF-IDF + Cosine Similarity",
        "composite_screening_score": "0.40 TF-IDF + 0.25 Skills + 0.15 Job Title + 0.10 Experience + 0.10 Education",
        "privacy_guarantee": "Demographic and protected characteristics (gender, age, race, address) are strictly excluded from ranking calculations."
    }


@app.post("/api/auth/login", tags=["Auth"])
async def login(payload: LoginRequest):
    """Demo-friendly authentication endpoint."""
    user = store.users.get(payload.email.lower())
    if not user:
        # Allow instant demo onboarding for any valid email format
        user = {
            "id": f"usr_{uuid.uuid4().hex[:6]}",
            "name": payload.email.split("@")[0].replace(".", " ").title(),
            "email": payload.email.lower(),
            "role": "Technical Recruiter",
            "company": "SomethingCo",
            "workspace": "SomethingCo Talent",
            "avatar_initials": payload.email[:2].upper(),
            "token": f"demo_token_{uuid.uuid4().hex[:8]}"
        }
        store.users[payload.email.lower()] = user

    return {
        "status": "success",
        "token": user["token"],
        "user": user
    }


@app.post("/api/auth/signup", tags=["Auth"])
async def signup(payload: SignupRequest):
    """Creates a new workspace user account."""
    user = {
        "id": f"usr_{uuid.uuid4().hex[:6]}",
        "name": f"{payload.first_name} {payload.last_name}".strip(),
        "email": payload.email.lower(),
        "role": "Hiring Lead",
        "company": payload.company,
        "workspace": f"{payload.company} Talent",
        "avatar_initials": f"{payload.first_name[:1]}{payload.last_name[:1]}".upper(),
        "token": f"demo_token_{uuid.uuid4().hex[:8]}"
    }
    store.users[payload.email.lower()] = user
    return {
        "status": "success",
        "token": user["token"],
        "user": user
    }


@app.get("/api/auth/me", tags=["Auth"])
async def get_current_user():
    """Returns default active session."""
    return {"user": list(store.users.values())[0]}


# -------------------------------------------------------------
# SaaS Workspace & Pipeline Endpoints
# -------------------------------------------------------------
@app.get("/api/dashboard", tags=["Workspace"])
async def get_dashboard_summary():
    """Returns command center metrics, recent activity, pipeline funnel, and top candidates."""
    total_candidates = len(store.candidates_pipeline)
    screened_candidates = len([c for c in store.candidates_pipeline if c["stage"] != "applied"])
    shortlisted = len([c for c in store.candidates_pipeline if c["stage"] in ["shortlisted", "interview", "offer", "hired"]])
    interviews = len([c for c in store.candidates_pipeline if c["stage"] == "interview"])
    offers = len([c for c in store.candidates_pipeline if c["stage"] == "offer"])
    hired = len([c for c in store.candidates_pipeline if c["stage"] == "hired"])

    funnel = [
        {"stage": "Applied", "count": total_candidates, "pct": 100},
        {"stage": "Screened", "count": screened_candidates, "pct": round(screened_candidates / total_candidates * 100, 1) if total_candidates > 0 else 0},
        {"stage": "Shortlisted", "count": shortlisted, "pct": round(shortlisted / total_candidates * 100, 1) if total_candidates > 0 else 0},
        {"stage": "Interview", "count": interviews, "pct": round(interviews / total_candidates * 100, 1) if total_candidates > 0 else 0},
        {"stage": "Offer", "count": offers, "pct": round(offers / total_candidates * 100, 1) if total_candidates > 0 else 0},
        {"stage": "Hired", "count": hired, "pct": round(hired / total_candidates * 100, 1) if total_candidates > 0 else 0}
    ]

    top_candidates = sorted(store.candidates_pipeline, key=lambda x: -x["score"])[:5]

    return {
        "kpis": {
            "open_roles": len([j for j in store.jobs if j["status"] == "Open"]),
            "active_candidates": total_candidates,
            "candidates_screened": screened_candidates,
            "interviews_pending": interviews,
            "avg_screening_score": 74.2
        },
        "funnel": funnel,
        "recent_activity": store.activity_log,
        "top_candidates": top_candidates,
        "jobs": store.jobs
    }


@app.get("/api/jobs", tags=["Jobs"])
async def list_jobs():
    """Lists all open, draft, and closed jobs."""
    return {"jobs": store.jobs, "total": len(store.jobs)}


@app.post("/api/jobs", tags=["Jobs"])
async def create_job(payload: CreateJobRequest):
    """Creates a new job posting in the workspace."""
    extracted = skill_extractor.extract_jd_skills(payload.description)
    req_skills = payload.required_skills if payload.required_skills else extracted["required_skills"]
    pref_skills = payload.preferred_skills if payload.preferred_skills else extracted["preferred_skills"]

    new_job = {
        "id": f"job_{len(store.jobs) + 1:02d}",
        "title": payload.title,
        "department": payload.department,
        "location": payload.location,
        "employment_type": payload.employment_type,
        "status": "Open",
        "hiring_manager": payload.hiring_manager,
        "filename": "",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "candidates_count": 0,
        "screened_count": 0,
        "required_skills": req_skills,
        "preferred_skills": pref_skills,
        "experience_req": payload.experience_req,
        "education_req": payload.education_req,
        "description": payload.description
    }
    store.jobs.insert(0, new_job)
    
    store.activity_log.insert(0, {
        "id": f"act_{len(store.activity_log)+1}",
        "action": "Job Created",
        "description": f"Created new opening for '{payload.title}'",
        "time": "Just now",
        "user": payload.hiring_manager
    })

    return {"status": "success", "job": new_job}


@app.get("/api/jobs/{job_id}", tags=["Jobs"])
async def get_job_detail(job_id: str):
    """Returns complete details, pipeline, and candidates for a specific job."""
    job = next((j for j in store.jobs if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    candidates = [c for c in store.candidates_pipeline if c.get("job_id") == job_id]
    return {
        "job": job,
        "candidates": candidates,
        "total_candidates": len(candidates)
    }


@app.get("/api/candidates", tags=["Candidates"])
async def list_candidates():
    """Lists all candidates across the organization."""
    return {"candidates": store.candidates_pipeline, "total": len(store.candidates_pipeline)}


@app.patch("/api/candidates/{candidate_id}/stage", tags=["Candidates"])
async def update_candidate_stage(candidate_id: str, payload: StageUpdateRequest):
    """Updates candidate recruiting pipeline stage (e.g. Move to Interview, Shortlist, Reject)."""
    cand = next((c for c in store.candidates_pipeline if c["id"] == candidate_id), None)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    valid_stages = {"applied", "screening", "shortlisted", "interview", "offer", "hired", "rejected"}
    new_stage = payload.stage.lower().strip()
    if new_stage not in valid_stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stage '{new_stage}'. Valid stages are: {', '.join(sorted(valid_stages))}"
        )

    old_stage = cand["stage"]
    cand["stage"] = new_stage

    store.activity_log.insert(0, {
        "id": f"act_{len(store.activity_log)+1}",
        "action": "Stage Updated",
        "description": f"{cand['name']} moved from {old_stage.title()} to {new_stage.title()}",
        "time": "Just now",
        "user": "Recruiter"
    })

    return {"status": "success", "candidate": cand}


@app.get("/api/analytics", tags=["Analytics"])
async def get_analytics_data():
    """Returns hiring metrics, skills demand, source breakdown, and score distribution."""
    return {
        "workspace_status": "Demo Workspace (Simulated Live Data)",
        "summary": {
            "total_applications": 38,
            "screened": 26,
            "shortlisted": 14,
            "interview_rate": "36.8%",
            "avg_time_to_screen": "1.4 days",
            "avg_screening_score": 72.5
        },
        "score_distribution": [
            {"tier": "Excellent (80-100%)", "count": 8, "pct": 30.8},
            {"tier": "Strong (65-79%)", "count": 10, "pct": 38.5},
            {"tier": "Moderate (45-64%)", "count": 5, "pct": 19.2},
            {"tier": "Low (<45%)", "count": 3, "pct": 11.5}
        ],
        "top_skills_demand": [
            {"skill": "Python", "count": 28, "category": "Programming"},
            {"skill": "FastAPI", "count": 22, "category": "Backend"},
            {"skill": "Docker", "count": 20, "category": "DevOps"},
            {"skill": "PyTorch", "count": 18, "category": "AI/ML"},
            {"skill": "PostgreSQL", "count": 16, "category": "Database"},
            {"skill": "Kubernetes", "count": 14, "category": "DevOps"},
            {"skill": "Scikit-Learn", "count": 14, "category": "AI/ML"}
        ],
        "sources": [
            {"source": "Direct Career Site", "candidates": 14, "conversion": "42%"},
            {"source": "LinkedIn Talent", "candidates": 12, "conversion": "38%"},
            {"source": "Internal Referral", "candidates": 8, "conversion": "62%"},
            {"source": "GitHub / Inbound", "candidates": 4, "conversion": "50%"}
        ]
    }


# -------------------------------------------------------------
# Core ML & Candidate Screening Endpoints
# -------------------------------------------------------------
@app.get("/api/skills-taxonomy", tags=["Configuration"])
async def get_skills_taxonomy():
    """Returns the configurable skill normalization taxonomy."""
    return {
        "taxonomy": skill_extractor.taxonomy,
        "total_skills": len(skill_extractor.taxonomy)
    }


@app.get("/api/sample-jobs", tags=["Data"])
async def get_sample_jobs():
    """Lists pre-packaged demonstration job descriptions."""
    if not os.path.exists(JD_DIR):
        return {"jobs": []}

    jobs = []
    for jd_file in sorted(os.listdir(JD_DIR)):
        if jd_file.endswith(".txt"):
            filepath = os.path.join(JD_DIR, jd_file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            first_line = content.splitlines()[0] if content else jd_file
            title = first_line.replace("Job Title:", "").strip()
            jd_skills = skill_extractor.extract_jd_skills(content)
            
            jobs.append({
                "filename": jd_file,
                "title": title,
                "content": content,
                "required_skills": jd_skills["required_skills"],
                "preferred_skills": jd_skills["preferred_skills"]
            })
    return {"jobs": jobs}


@app.get("/api/sample-resumes", tags=["Data"])
async def get_sample_resumes():
    """Lists pre-packaged demonstration resumes."""
    if not os.path.exists(RESUMES_DIR):
        return {"resumes": []}

    resumes = []
    for fname in sorted(os.listdir(RESUMES_DIR)):
        if fname.startswith("."):
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext in [".pdf", ".docx", ".txt"]:
            resumes.append({
                "file_name": fname,
                "file_type": ext.replace(".", "").upper()
            })
    return {"resumes": resumes, "total": len(resumes)}


@app.post("/api/rank-sample-data", tags=["Ranking"])
async def rank_sample_data(job_filename: str = Form("job_01_senior_ai_ml_engineer.txt")):
    """
    Ranks the pre-packaged sample resumes against a chosen sample job description.
    Safely resolves files and executes TF-IDF + composite screening ranking.
    """
    jd_path = _safe_resolve_job_file(job_filename)

    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    parsed_resumes = []
    for fname in sorted(os.listdir(RESUMES_DIR)):
        if fname.startswith("."):
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext in [".pdf", ".docx", ".txt"]:
            fpath = os.path.join(RESUMES_DIR, fname)
            try:
                parsed = parse_resume(fpath, fname)
                parsed_resumes.append(parsed)
            except Exception:
                continue

    if not parsed_resumes:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No sample resumes could be parsed."
        )

    ranker = ResumeRanker()
    ranked_candidates = ranker.rank_candidates(jd_text, parsed_resumes)
    jd_skills = skill_extractor.extract_jd_skills(jd_text)

    return {
        "job_title": jd_text.splitlines()[0].replace("Job Title:", "").strip(),
        "job_description_length": len(jd_text),
        "total_candidates": len(ranked_candidates),
        "jd_skills_profile": jd_skills,
        "ranked_candidates": ranked_candidates
    }


@app.post("/rank", tags=["Ranking"])
async def rank_resumes_multipart(
    job_description_text: Optional[str] = Form(None),
    job_description_file: Optional[UploadFile] = File(None),
    resumes: List[UploadFile] = File(...)
):
    """
    Primary multi-part endpoint for uploading multiple resumes and a job description.
    Enforces strict file size limits and filename sanitization.
    """
    if len(resumes) > MAX_RESUMES_BATCH_COUNT:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Too many resumes submitted. Maximum allowed per batch is {MAX_RESUMES_BATCH_COUNT}."
        )

    jd_content = ""
    if job_description_text and job_description_text.strip():
        if len(job_description_text) > MAX_TEXT_INPUT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job description exceeds maximum text limit of {MAX_TEXT_INPUT_LENGTH} characters."
            )
        jd_content = job_description_text.strip()
    elif job_description_file:
        file_bytes = await job_description_file.read()
        if len(file_bytes) > MAX_JD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Job description file exceeds size limit ({MAX_JD_SIZE_BYTES // (1024*1024)}MB)."
            )
        fname = _sanitize_filename(job_description_file.filename or "job_description.txt")
        try:
            parsed_jd = parse_resume(file_bytes, fname)
            jd_content = parsed_jd["raw_text"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse uploaded job description: {str(e)}"
            )

    if not jd_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a job description as text or upload a job description file."
        )

    if not resumes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload at least one resume file."
        )

    parsed_resumes = []
    errors = []

    for i, file_obj in enumerate(resumes):
        fname = _sanitize_filename(file_obj.filename or f"resume_{i+1}.txt")
        try:
            content_bytes = await file_obj.read()
            if not content_bytes:
                errors.append(f"File '{fname}' is empty (0 bytes).")
                continue
            if len(content_bytes) > MAX_FILE_SIZE_BYTES:
                errors.append(f"File '{fname}' exceeds {MAX_FILE_SIZE_BYTES // (1024*1024)}MB limit.")
                continue
            parsed = parse_resume(content_bytes, fname)
            parsed["candidate_id"] = f"CAND-{i+1:03d}"
            parsed_resumes.append(parsed)
        except UnsupportedFormatError as ufe:
            errors.append(f"{fname}: {str(ufe)}")
        except FileExtractionError as fee:
            errors.append(f"{fname}: {str(fee)}")
        except Exception as ex:
            errors.append(f"{fname}: Extraction error: {str(ex)}")

    if not parsed_resumes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No valid resumes could be processed. Errors: {'; '.join(errors)}"
        )

    try:
        ranker = ResumeRanker()
        ranked_candidates = ranker.rank_candidates(jd_content, parsed_resumes)
        jd_skills = skill_extractor.extract_jd_skills(jd_content)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ranking execution failed: {str(e)}"
        )

    return {
        "status": "success",
        "total_resumes_submitted": len(resumes),
        "total_resumes_processed": len(ranked_candidates),
        "processing_warnings": errors,
        "jd_skills_profile": jd_skills,
        "ranked_candidates": ranked_candidates
    }


@app.post("/rank-raw-text", tags=["Ranking"])
async def rank_resumes_raw_text(payload: RankJsonRequest):
    """JSON API endpoint for programmatic screening using raw strings."""
    resumes_data = []
    for i, r in enumerate(payload.resumes):
        resumes_data.append({
            "candidate_id": r.candidate_id or f"CAND-{i+1:03d}",
            "candidate_name": r.candidate_name or f"Candidate {i+1}",
            "file_name": _sanitize_filename(r.file_name or f"resume_{i+1}.txt"),
            "file_type": "TXT",
            "raw_text": r.raw_text,
            "snippet": r.raw_text[:250].replace("\n", " ").strip() + "..."
        })

    ranker = ResumeRanker()
    try:
        ranked_candidates = ranker.rank_candidates(payload.job_description, resumes_data)
        jd_skills = skill_extractor.extract_jd_skills(payload.job_description)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {
        "status": "success",
        "total_candidates": len(ranked_candidates),
        "jd_skills_profile": jd_skills,
        "ranked_candidates": ranked_candidates
    }


@app.get("/api/export-csv", tags=["Export"])
async def export_candidates_csv(job_filename: str = "job_01_senior_ai_ml_engineer.txt"):
    """Exports ranked candidate results as a structured CSV file with directory traversal defense."""
    jd_path = _safe_resolve_job_file(job_filename)

    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    parsed_resumes = []
    for fname in sorted(os.listdir(RESUMES_DIR)):
        if fname.startswith("."):
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext in [".pdf", ".docx", ".txt"]:
            fpath = os.path.join(RESUMES_DIR, fname)
            try:
                parsed = parse_resume(fpath, fname)
                parsed_resumes.append(parsed)
            except Exception:
                continue

    ranker = ResumeRanker()
    ranked = ranker.rank_candidates(jd_text, parsed_resumes)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Rank", "Candidate ID", "Candidate Name", "File Name", "File Type",
        "Screening Score (%)", "TF-IDF Cosine Match (%)", "Skill Coverage (%)",
        "Title Match (%)", "Experience Match (%)", "Education Match (%)",
        "ATS Parseability (%)", "ATS Grade", "Matched Skills",
        "Missing Required Skills", "Missing Preferred Skills",
        "Highest Degree", "Primary Discipline", "Total Experience (Yrs)", "Explainability"
    ])

    for c in ranked:
        writer.writerow([
            c["rank"],
            c["candidate_id"],
            c["candidate_name"],
            c["file_name"],
            c["file_type"],
            c["screening_score"],
            c["score_percentage"],
            c["skill_coverage_pct"],
            c["title_match_pct"],
            c["experience_match_pct"],
            c["education_match_pct"],
            c["ats_parseability"]["parseability_score"],
            c["ats_parseability"]["parseability_grade"],
            "; ".join(c["matched_skills"]),
            "; ".join(c["missing_required"]),
            "; ".join(c["missing_preferred"]),
            c["highest_degree"],
            c["primary_discipline"],
            c["total_years_experience"],
            c["explainability"]
        ])

    output.seek(0)
    clean_csv_name = os.path.basename(job_filename).replace(".txt", "")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=candidate_rankings_{clean_csv_name}.csv"}
    )


# -------------------------------------------------------------
# Frontend Static Files & SPA Deep Linking Fallbacks
# -------------------------------------------------------------
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    @app.get("/login", include_in_schema=False)
    @app.get("/signup", include_in_schema=False)
    @app.get("/app", include_in_schema=False)
    @app.get("/app/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(full_path: Optional[str] = None):
        """Serves SPA frontend index.html with HTML5 pushState support."""
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
