"""
Multi-Factor Candidate Matcher Module
Computes transparent sub-scores for:
1. Job Title Match
2. Experience Match (with explicit uncertainty handling)
3. Education & Discipline Match
"""

import re
from typing import Dict, Any, List, Optional, Tuple

DEGREE_RANKS = {
    "PhD": 4,
    "Master's": 3,
    "Bachelor's": 2,
    "Associate's": 1,
    "High School": 0,
    "Not Specified": 0
}

TECHNICAL_DISCIPLINES = {
    "computer science", "software engineering", "data science", "artificial intelligence",
    "machine learning", "information technology", "electrical engineering", "computer engineering",
    "mathematics", "statistics", "physics", "computer science / general"
}


def extract_target_job_title(jd_text: str) -> str:
    """Extracts job title from the first lines or header of JD text."""
    if not jd_text:
        return "Target Role"

    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
    for line in lines[:3]:
        if line.lower().startswith("job title:"):
            return line.split(":", 1)[1].strip()
        if any(w in line.lower() for w in ["engineer", "developer", "scientist", "analyst", "specialist", "architect"]):
            return line[:50]

    return lines[0][:50] if lines else "Target Role"


def match_job_title(target_job_title: str, candidate_job_titles: List[str]) -> Dict[str, Any]:
    """
    Evaluates similarity between the target JD job title and candidate past job titles.
    """
    if not target_job_title or not candidate_job_titles:
        return {
            "title_match_score": 0.3,
            "title_match_percentage": 30.0,
            "target_title": target_job_title or "Not Specified",
            "best_matched_title": "None detected",
            "status": "No Previous Titles Detected"
        }

    def tokenize_title(t: str) -> set:
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", t.lower())
        tokens = set(clean.split())
        # Replace common synonyms
        synonyms = {"ml": "machine learning", "ai": "artificial intelligence", "sr": "senior", "dev": "developer"}
        expanded = set()
        for tok in tokens:
            if tok in synonyms:
                expanded.update(synonyms[tok].split())
            else:
                expanded.add(tok)
        return expanded - {"and", "or", "the", "a", "of", "in", "for"}

    target_tokens = tokenize_title(target_job_title)
    if not target_tokens:
        target_tokens = {"engineer"}

    best_score = 0.0
    best_title = candidate_job_titles[0]

    for c_title in candidate_job_titles:
        c_tokens = tokenize_title(c_title)
        if not c_tokens:
            continue

        overlap = target_tokens.intersection(c_tokens)
        union = target_tokens.union(c_tokens)
        jaccard = len(overlap) / len(union) if union else 0.0
        
        # Check core role noun overlap (e.g. engineer, developer, scientist, analyst)
        core_nouns = {"engineer", "developer", "scientist", "analyst", "specialist", "architect", "lead", "writer", "accountant"}
        has_core_noun = len(overlap.intersection(core_nouns)) > 0

        score = jaccard
        if has_core_noun:
            coverage = max(len(overlap) / len(c_tokens), len(overlap) / len(target_tokens))
            score = max(score, coverage * 0.9)

        if score > best_score:
            best_score = score
            best_title = c_title

    best_score = max(0.0, min(1.0, best_score))

    if best_score >= 0.60:
        status = "Direct Role Match"
    elif best_score >= 0.30:
        status = "Related Role Match"
    else:
        status = "Different Domain / Role Discrepancy"

    return {
        "title_match_score": round(best_score, 4),
        "title_match_percentage": round(best_score * 100, 1),
        "target_title": target_job_title,
        "best_matched_title": best_title,
        "status": status
    }


def extract_required_experience_years(jd_text: str) -> float:
    """Extracts explicit years of experience required from JD."""
    if not jd_text:
        return 3.0

    exp_regex = re.compile(
        r"(\d+(?:\.\d+)?)\+?\s*(?:-\s*\d+\s*)?years?(?:\s+of)?(?:\s+(?:relevant|hands-on|professional|work))?\s+experience",
        re.IGNORECASE
    )
    match = exp_regex.search(jd_text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return 3.0 # Default benchmark requirement


def match_experience(
    jd_text: str,
    candidate_years: float,
    is_uncertain: bool
) -> Dict[str, Any]:
    """
    Evaluates candidate years of experience against explicit JD requirements.
    """
    req_years = extract_required_experience_years(jd_text)

    if is_uncertain or candidate_years == 0.0:
        return {
            "experience_match_score": 0.5,
            "experience_match_percentage": 50.0,
            "required_years": req_years,
            "candidate_years": 0.0,
            "is_uncertain": True,
            "status": "Not enough evidence (Uncertain)",
            "explanation": "Dates or total tenure could not be unambiguously extracted from resume text."
        }

    ratio = candidate_years / max(1.0, req_years)
    score = min(1.0, ratio)

    if candidate_years >= req_years:
        status = f"Meets/Exceeds Requirement ({candidate_years} yrs vs {req_years} yrs req)"
    else:
        status = f"Below Requirement ({candidate_years} yrs vs {req_years} yrs req)"

    return {
        "experience_match_score": round(score, 4),
        "experience_match_percentage": round(score * 100, 1),
        "required_years": req_years,
        "candidate_years": candidate_years,
        "is_uncertain": False,
        "status": status,
        "explanation": f"Candidate possesses {candidate_years} years estimated experience vs {req_years} years requested in JD."
    }


def match_education(
    jd_text: str,
    highest_degree: str,
    discipline: str
) -> Dict[str, Any]:
    """
    Evaluates candidate highest degree and discipline alignment against JD requirements.
    """
    # Detect JD requirement
    req_degree = "Bachelor's"
    if re.search(r"\b(?:master|m\.s\.|m\.sc\.|phd|ph\.d\.|doctorate)\b", jd_text, re.IGNORECASE):
        if re.search(r"\b(?:phd|ph\.d\.|doctorate)\b", jd_text, re.IGNORECASE):
            req_degree = "PhD"
        else:
            req_degree = "Master's"

    cand_rank = DEGREE_RANKS.get(highest_degree, 0)
    req_rank = DEGREE_RANKS.get(req_degree, 2)

    # Check discipline relevance
    is_tech_discipline = discipline.lower().strip() in TECHNICAL_DISCIPLINES
    is_business_role = any(r in jd_text.lower() for r in ["accountant", "marketing", "cpa", "finance"])

    disc_aligned = True
    if is_business_role:
        disc_aligned = any(d in discipline.lower() for d in ["accounting", "finance", "business", "marketing"])
    else:
        disc_aligned = is_tech_discipline

    # Compute education score
    if cand_rank >= req_rank:
        if disc_aligned:
            score = 1.0
            status = f"Meets/Exceeds Requirement ({highest_degree} in {discipline})"
        else:
            score = 0.50
            status = f"Degree Level Met but Discipline Mismatch ({highest_degree} in {discipline})"
    elif cand_rank > 0:
        if disc_aligned:
            score = 0.70
            status = f"Degree Level Below Target ({highest_degree} vs {req_degree} Req in {discipline})"
        else:
            score = 0.30
            status = f"Degree Level & Discipline Mismatch ({highest_degree} in {discipline})"
    else:
        score = 0.20
        status = "No Formal Degree Detected"

    return {
        "education_match_score": round(score, 4),
        "education_match_percentage": round(score * 100, 1),
        "required_degree": req_degree,
        "candidate_degree": highest_degree,
        "candidate_discipline": discipline,
        "is_discipline_aligned": disc_aligned,
        "status": status
    }
