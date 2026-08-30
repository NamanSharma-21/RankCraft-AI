"""
Structured Resume Parser & ATS Parseability Inspector
Extracts candidate profile fields (Name, Email, Phone, Summary, Skills, Work Experience,
Education, Certifications) and performs an 8-point ATS Parseability audit.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from backend.skill_extractor import skill_extractor

# Regex patterns for contact information
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")

# Regex patterns for degrees
DEGREE_LEVELS = [
    ("PhD", re.compile(r"\b(?:ph\.?d\.?|doctor of philosophy|doctorate)\b", re.IGNORECASE)),
    ("Master's", re.compile(r"\b(?:master(?:'s)?|m\.s\.?|m\.sc\.?|m\.tech\.?|mba)\b", re.IGNORECASE)),
    ("Bachelor's", re.compile(r"\b(?:bachelor(?:'s)?|b\.s\.?|b\.sc\.?|b\.tech\.?|b\.e\.?|b\.a\.?|undergraduate)\b", re.IGNORECASE)),
    ("Associate's", re.compile(r"\b(?:associate(?:'s)?|a\.s\.?|a\.a\.?|diploma)\b", re.IGNORECASE)),
    ("High School", re.compile(r"\b(?:high school|secondary school|ged)\b", re.IGNORECASE))
]

DISCIPLINES = [
    "Computer Science", "Software Engineering", "Data Science", "Artificial Intelligence",
    "Machine Learning", "Information Technology", "Electrical Engineering", "Computer Engineering",
    "Mathematics", "Statistics", "Physics", "Business Administration", "Economics",
    "Accounting", "Finance", "Marketing", "Communications", "Technical Writing"
]

KNOWN_CERTS = [
    "AWS Certified Solutions Architect", "AWS Certified Machine Learning", "AWS Certified Developer",
    "Google Cloud Professional Data Engineer", "Google Cloud Professional ML Engineer",
    "Azure Solutions Architect", "Azure Data Scientist Associate", "Certified Kubernetes Administrator (CKA)",
    "TensorFlow Developer Certificate", "PMP", "Certified Scrum Master (CSM)", "CPA",
    "Certified Information Systems Security Professional (CISSP)", "CompTIA Security+"
]


def extract_contact_info(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extracts email and phone number from text."""
    email_match = EMAIL_REGEX.search(text)
    email = email_match.group(0) if email_match else None

    phone_match = PHONE_REGEX.search(text)
    phone = phone_match.group(0) if phone_match else None

    return email, phone


def extract_summary(text: str) -> Optional[str]:
    """Extracts candidate professional summary or objective if present."""
    pattern = re.compile(
        r"(?:professional summary|summary|career objective|objective|profile|about me):?\s*\n(.*?)(?=\n\s*(?:skills|experience|work history|education|projects|certifications)|\Z)",
        re.IGNORECASE | re.DOTALL
    )
    match = pattern.search(text)
    if match:
        summary_text = match.group(1).strip()
        # Return first 300 chars clean
        return " ".join(summary_text.split()[:80])
    
    # Fallback: check first 3 lines if no explicit section
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[1:4]:
        if len(line.split()) >= 8 and not EMAIL_REGEX.search(line) and not PHONE_REGEX.search(line):
            return line
    return None


def extract_work_experience(text: str) -> Tuple[List[Dict[str, Any]], float, bool]:
    """
    Extracts structured work experience items and calculates estimated years of experience.
    Returns: (list of roles, total_years_estimated, is_uncertain_flag)
    """
    roles = []
    total_years = 0.0
    is_uncertain = False

    # Check for explicit experience statement (e.g. "6+ years of experience in ML")
    explicit_pattern = re.compile(r"(\d+(?:\.\d+)?)\+?\s*years?(?:\s+of)?(?:\s+hands-on)?\s+experience", re.IGNORECASE)
    explicit_match = explicit_pattern.search(text)
    if explicit_match:
        try:
            total_years = float(explicit_match.group(1))
        except ValueError:
            pass

    # Extract Experience section
    exp_pattern = re.compile(
        r"(?:work experience|professional experience|experience|employment history):?\s*\n(.*?)(?=\n\s*(?:education|skills|projects|certifications|awards)|\Z)",
        re.IGNORECASE | re.DOTALL
    )
    match = exp_pattern.search(text)
    exp_section = match.group(1) if match else text

    # Regex to find date ranges: e.g. 2018 - 2024, Jan 2020 - Present, 2019 – Present
    date_range_regex = re.compile(
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+)?(\d{4})\s*(?:-|–|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+)?(\d{4}|Present|Current)",
        re.IGNORECASE
    )

    current_year = 2026 # Academic simulation anchor year
    year_spans = []

    for d_match in date_range_regex.finditer(exp_section):
        start_year = int(d_match.group(2))
        end_str = d_match.group(4)
        if end_str.lower() in ["present", "current"]:
            end_year = current_year
        else:
            try:
                end_year = int(end_str)
            except ValueError:
                end_year = start_year + 1

        span = max(0.5, float(end_year - start_year))
        year_spans.append((start_year, end_year, span))

    # Parse role lines around date matches
    lines = [l.strip() for l in exp_section.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        d_search = date_range_regex.search(line)
        if d_search:
            title_candidate = lines[i-1] if i > 0 else line
            # Clean title
            title_candidate = re.sub(r"^(?:•|\*|-|\d+\.)\s*", "", title_candidate).strip()
            roles.append({
                "job_title": title_candidate[:60],
                "dates": d_search.group(0),
                "duration_years": round(year_spans[len(roles)][2], 1) if len(roles) < len(year_spans) else 1.0
            })

    if year_spans and total_years == 0.0:
        # Avoid double-counting overlapping spans; calculate range span
        min_start = min(s[0] for s in year_spans)
        max_end = max(s[1] for s in year_spans)
        total_years = float(max_end - min_start)
    elif not year_spans and total_years == 0.0:
        is_uncertain = True
        total_years = 0.0

    return roles, round(total_years, 1), is_uncertain


def extract_education(text: str) -> Tuple[List[Dict[str, Any]], str, str]:
    """
    Extracts education degrees, discipline, and detects highest degree level.
    Returns: (list of degree items, highest_degree_level, primary_discipline)
    """
    degrees = []
    highest_level = "Not Specified"
    primary_discipline = "Not Specified"

    # Check for degrees across text
    for level_name, pattern in DEGREE_LEVELS:
        if pattern.search(text):
            if highest_level == "Not Specified":
                highest_level = level_name
            
            # Search for discipline near the degree mention
            found_discipline = "Computer Science / General"
            for disc in DISCIPLINES:
                if re.search(rf"\b{re.escape(disc)}\b", text, re.IGNORECASE):
                    found_discipline = disc
                    if primary_discipline == "Not Specified":
                        primary_discipline = disc
                    break

            degrees.append({
                "degree_level": level_name,
                "discipline": found_discipline
            })

    return degrees, highest_level, primary_discipline


def extract_certifications(text: str) -> List[str]:
    """Extracts recognized professional certifications."""
    found_certs = []
    for cert in KNOWN_CERTS:
        if re.search(rf"\b{re.escape(cert)}\b", text, re.IGNORECASE):
            found_certs.append(cert)
    return found_certs


def evaluate_ats_parseability(
    raw_text: str,
    name: Optional[str],
    email: Optional[str],
    phone: Optional[str],
    skills: List[str],
    roles: List[Dict[str, Any]],
    total_years: float,
    highest_degree: str
) -> Dict[str, Any]:
    """
    Performs an 8-point ATS Parseability check and computes an ATS health score (0-100).
    """
    checks = []
    score = 0

    # 1. Text Extraction (15 pts)
    word_count = len(raw_text.split())
    if word_count >= 50:
        checks.append({"item": "Text Extraction", "status": "pass", "points": 15, "note": f"Extracted {word_count} words cleanly."})
        score += 15
    elif word_count > 0:
        checks.append({"item": "Text Extraction", "status": "warn", "points": 8, "note": f"Low word count ({word_count} words)."})
        score += 8
    else:
        checks.append({"item": "Text Extraction", "status": "fail", "points": 0, "note": "Empty extraction (image-only or corrupt file)."})

    # 2. Candidate Name (10 pts)
    if name and name != "Candidate":
        checks.append({"item": "Candidate Name", "status": "pass", "points": 10, "note": f"Detected: {name}"})
        score += 10
    else:
        checks.append({"item": "Candidate Name", "status": "warn", "points": 4, "note": "Name extracted from fallback filename."})
        score += 4

    # 3. Email (10 pts)
    if email:
        checks.append({"item": "Email Contact", "status": "pass", "points": 10, "note": f"Detected: {email}"})
        score += 10
    else:
        checks.append({"item": "Email Contact", "status": "fail", "points": 0, "note": "No valid email address found."})

    # 4. Phone Number (10 pts)
    if phone:
        checks.append({"item": "Phone Contact", "status": "pass", "points": 10, "note": f"Detected: {phone}"})
        score += 10
    else:
        checks.append({"item": "Phone Contact", "status": "fail", "points": 0, "note": "No phone number detected."})

    # 5. Work Experience Section (15 pts)
    if roles:
        checks.append({"item": "Experience Section", "status": "pass", "points": 15, "note": f"Parsed {len(roles)} employment role(s)."})
        score += 15
    elif re.search(r"experience", raw_text, re.IGNORECASE):
        checks.append({"item": "Experience Section", "status": "warn", "points": 8, "note": "Experience mentions found but roles unformatted."})
        score += 8
    else:
        checks.append({"item": "Experience Section", "status": "fail", "points": 0, "note": "No work experience section identified."})

    # 6. Timeline / Dates (15 pts)
    if total_years > 0:
        checks.append({"item": "Timeline & Dates", "status": "pass", "points": 15, "note": f"Estimated {total_years} years total tenure."})
        score += 15
    else:
        checks.append({"item": "Timeline & Dates", "status": "fail", "points": 0, "note": "Dates could not be reliably calculated."})

    # 7. Education & Degree (15 pts)
    if highest_degree != "Not Specified":
        checks.append({"item": "Education Section", "status": "pass", "points": 15, "note": f"Detected: {highest_degree} degree."})
        score += 15
    else:
        checks.append({"item": "Education Section", "status": "fail", "points": 0, "note": "No formal degree detected."})

    # 8. Technical Skills (10 pts)
    if len(skills) >= 4:
        checks.append({"item": "Skill Extraction", "status": "pass", "points": 10, "note": f"Extracted {len(skills)} canonical skills."})
        score += 10
    elif len(skills) > 0:
        checks.append({"item": "Skill Extraction", "status": "warn", "points": 5, "note": f"Extracted only {len(skills)} skill(s)."})
        score += 5
    else:
        checks.append({"item": "Skill Extraction", "status": "fail", "points": 0, "note": "No matching skills identified."})

    # Grade determination
    if score >= 85:
        grade = "High Parseability"
        badge_class = "badge-pass"
    elif score >= 65:
        grade = "Moderate Parseability"
        badge_class = "badge-warn"
    else:
        grade = "Low Parseability"
        badge_class = "badge-fail"

    return {
        "parseability_score": score,
        "parseability_grade": grade,
        "badge_class": badge_class,
        "checklist": checks
    }


def parse_structured_resume(raw_text: str, candidate_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Full structured resume parser entrypoint.
    Returns rich candidate profile and ATS parseability evaluation.
    """
    email, phone = extract_contact_info(raw_text)
    summary = extract_summary(raw_text)
    skills = skill_extractor.extract_skills(raw_text)
    roles, total_years, is_uncertain_exp = extract_work_experience(raw_text)
    degrees, highest_degree, primary_discipline = extract_education(raw_text)
    certifications = extract_certifications(raw_text)

    # Job titles extracted
    job_titles = [r["job_title"] for r in roles if r.get("job_title")]
    if not job_titles:
        # Heuristic fallback: check first lines for title
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        for l in lines[:4]:
            if any(term in l.lower() for term in ["engineer", "developer", "scientist", "analyst", "specialist", "accountant", "writer", "administrator", "lead", "manager"]):
                job_titles.append(l)
                break

    ats_audit = evaluate_ats_parseability(
        raw_text=raw_text,
        name=candidate_name,
        email=email,
        phone=phone,
        skills=skills,
        roles=roles,
        total_years=total_years,
        highest_degree=highest_degree
    )

    return {
        "candidate_name": candidate_name or "Candidate",
        "email": email,
        "phone": phone,
        "summary": summary,
        "skills": skills,
        "work_experience": roles,
        "job_titles": job_titles,
        "total_years_experience": total_years,
        "is_experience_uncertain": is_uncertain_exp,
        "education": degrees,
        "highest_degree": highest_degree,
        "primary_discipline": primary_discipline,
        "certifications": certifications,
        "ats_parseability": ats_audit
    }
