"""
Ranking & Multi-Factor Scoring Engine
AI Resume Screening & Candidate Ranking System

Combines:
1. Core TF-IDF Feature Space + Cosine Similarity (Required Academic ML Foundation)
2. Deterministic Skill Coverage Matching (Required vs Preferred)
3. Job Title Alignment
4. Experience Duration Match (with uncertainty reporting)
5. Education Degree & Discipline Match
6. ATS Parseability Audit
7. Composite 'Screening Score' (Project-Defined Composite Metric)
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.preprocessing import preprocess_text
from backend.skill_extractor import skill_extractor
from backend.structured_parser import parse_structured_resume
from backend.matcher import (
    extract_target_job_title,
    match_job_title,
    match_experience,
    match_education
)


class ResumeRanker:
    """
    Ranks resumes against a target job description using TF-IDF cosine similarity
    and multi-factor candidate profiling.
    """

    def __init__(
        self,
        ngram_range: tuple = (1, 2),
        min_df: int = 1,
        sublinear_tf: bool = True,
        # Transparent weights for the project-defined Screening Score
        weight_tfidf: float = 0.40,
        weight_skills: float = 0.25,
        weight_title: float = 0.15,
        weight_experience: float = 0.10,
        weight_education: float = 0.10
    ):
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.sublinear_tf = sublinear_tf
        self.weight_tfidf = weight_tfidf
        self.weight_skills = weight_skills
        self.weight_title = weight_title
        self.weight_experience = weight_experience
        self.weight_education = weight_education
        self.vectorizer: Optional[TfidfVectorizer] = None

    def rank_candidates(
        self,
        job_description: str,
        resumes: List[Dict[str, Any]],
        top_k_features: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Ranks a list of candidate resumes against one job description.
        """
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty.")
        if not resumes:
            return []

        # Step 1: Preprocess Job Description & Extract JD Skills Profile
        clean_jd = preprocess_text(job_description)
        if not clean_jd.strip():
            raise ValueError("Job description contains no usable text after preprocessing.")

        target_job_title = extract_target_job_title(job_description)
        jd_skills_profile = skill_extractor.extract_jd_skills(job_description)

        # Step 2: Parse structured profiles & clean text for all resumes
        structured_resumes = []
        clean_resumes = []

        for i, r in enumerate(resumes):
            raw_text = r.get("raw_text", "")
            cand_name = r.get("candidate_name") or f"Candidate {i+1}"
            
            # Structured extraction
            structured_profile = parse_structured_resume(raw_text, cand_name)
            
            # Preprocess text for TF-IDF
            clean_text = r.get("clean_text") or preprocess_text(raw_text)
            clean_resumes.append(clean_text)

            structured_resumes.append({
                "candidate_id": r.get("candidate_id", f"CAND-{i+1:03d}"),
                "candidate_name": cand_name,
                "file_name": r.get("file_name", f"resume_{i+1}.txt"),
                "file_type": r.get("file_type", "TXT"),
                "raw_text": raw_text,
                "snippet": r.get("snippet", raw_text[:250].replace("\n", " ").strip() + "..."),
                "word_count": r.get("word_count", len(raw_text.split())),
                "profile": structured_profile
            })

        # Step 3: TF-IDF Vectorization across common feature space
        corpus = [clean_jd] + clean_resumes
        self.vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            sublinear_tf=self.sublinear_tf,
            token_pattern=r"(?u)\b\w+\b"
        )
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        feature_names = np.array(self.vectorizer.get_feature_names_out())

        jd_vec = tfidf_matrix[0]
        resume_vecs = tfidf_matrix[1:]

        # Step 4: Compute Directional Cosine Similarity
        sim_scores = cosine_similarity(jd_vec, resume_vecs).flatten()

        jd_dense = jd_vec.toarray().flatten()
        top_jd_indices = np.argsort(jd_dense)[::-1]
        top_jd_keywords = [
            feature_names[idx] for idx in top_jd_indices if jd_dense[idx] > 0
        ][:15]

        results = []
        for i, s_res in enumerate(structured_resumes):
            profile = s_res["profile"]

            # 1. TF-IDF Score
            tfidf_score = float(sim_scores[i])
            tfidf_score = max(0.0, min(1.0, tfidf_score))
            tfidf_pct = round(tfidf_score * 100, 2)

            # Extract TF-IDF lexical matched features
            res_vec_dense = resume_vecs[i].toarray().flatten()
            overlap_weights = jd_dense * res_vec_dense
            top_overlap_indices = np.argsort(overlap_weights)[::-1]
            
            tfidf_matched_terms = []
            for idx in top_overlap_indices:
                if overlap_weights[idx] > 0 and len(tfidf_matched_terms) < top_k_features:
                    tfidf_matched_terms.append(feature_names[idx])

            # 2. Skill Matching (Required vs Preferred)
            skill_match_res = skill_extractor.match_skills(profile["skills"], jd_skills_profile)
            skill_score = skill_match_res["skill_coverage_ratio"]
            skill_pct = skill_match_res["skill_coverage_percentage"]

            # 3. Job Title Matching
            title_match_res = match_job_title(target_job_title, profile["job_titles"])
            title_score = title_match_res["title_match_score"]
            title_pct = title_match_res["title_match_percentage"]

            # 4. Experience Matching
            exp_match_res = match_experience(
                job_description,
                profile["total_years_experience"],
                profile["is_experience_uncertain"]
            )
            exp_score = exp_match_res["experience_match_score"]
            exp_pct = exp_match_res["experience_match_percentage"]

            # 5. Education Matching
            edu_match_res = match_education(
                job_description,
                profile["highest_degree"],
                profile["primary_discipline"]
            )
            edu_score = edu_match_res["education_match_score"]
            edu_pct = edu_match_res["education_match_percentage"]

            # 6. Composite Project-Defined "Screening Score"
            composite_score = (
                (self.weight_tfidf * tfidf_score) +
                (self.weight_skills * skill_score) +
                (self.weight_title * title_score) +
                (self.weight_experience * exp_score) +
                (self.weight_education * edu_score)
            )
            composite_score = max(0.0, min(1.0, composite_score))
            composite_pct = round(composite_score * 100, 1)

            # 7. Generate Natural Language Explainability
            explainability_summary = self._generate_explainability_narrative(
                candidate_name=s_res["candidate_name"],
                composite_pct=composite_pct,
                tfidf_pct=tfidf_pct,
                skill_match=skill_match_res,
                title_match=title_match_res,
                exp_match=exp_match_res,
                edu_match=edu_match_res
            )

            results.append({
                "candidate_id": s_res["candidate_id"],
                "candidate_name": s_res["candidate_name"],
                "file_name": s_res["file_name"],
                "file_type": s_res["file_type"],
                
                # Primary Composite Screening Score
                "screening_score": composite_pct,
                "screening_score_ratio": round(composite_score, 4),
                
                # Required TF-IDF Statistical Metric
                "similarity_score": round(tfidf_score, 4),
                "score_percentage": tfidf_pct,
                "tfidf_matched_terms": tfidf_matched_terms,
                
                # Multi-Factor Match Breakdown
                "skill_coverage_pct": skill_pct,
                "title_match_pct": title_pct,
                "experience_match_pct": exp_pct,
                "education_match_pct": edu_pct,
                
                # Detailed Skill Breakdown
                "matched_skills": skill_match_res["matched_skills"],
                "matched_required": skill_match_res["matched_required"],
                "missing_required": skill_match_res["missing_required"],
                "matched_preferred": skill_match_res["matched_preferred"],
                "missing_preferred": skill_match_res["missing_preferred"],
                "skill_classification_confidence": skill_match_res["classification_confidence"],
                
                # Detailed Alignment Breakdown
                "job_title_status": title_match_res["status"],
                "experience_status": exp_match_res["status"],
                "is_experience_uncertain": exp_match_res["is_uncertain"],
                "education_status": edu_match_res["status"],
                "highest_degree": profile["highest_degree"],
                "primary_discipline": profile["primary_discipline"],
                "total_years_experience": profile["total_years_experience"],
                
                # ATS Parseability
                "ats_parseability": profile["ats_parseability"],
                
                # Explainability & Structured Data
                "explainability": explainability_summary,
                "structured_profile": profile,
                "snippet": s_res["snippet"],
                "word_count": s_res["word_count"]
            })

        # Step 5: Deterministic Sort by Composite Screening Score, then TF-IDF Cosine, then Candidate ID
        results.sort(
            key=lambda x: (
                -x["screening_score"],
                -x["similarity_score"],
                x["candidate_id"]
            )
        )

        # Step 6: Assign Ranks 1..N
        for rank_idx, cand in enumerate(results, start=1):
            cand["rank"] = rank_idx

        return results

    def _generate_explainability_narrative(
        self,
        candidate_name: str,
        composite_pct: float,
        tfidf_pct: float,
        skill_match: Dict[str, Any],
        title_match: Dict[str, Any],
        exp_match: Dict[str, Any],
        edu_match: Dict[str, Any]
    ) -> str:
        """
        Builds a human-readable explanation of the candidate's ranking rationale.
        """
        strengths = []
        gaps = []

        if skill_match["matched_required"]:
            top_skills = ", ".join(skill_match["matched_required"][:4])
            strengths.append(f"Strong required skill alignment ({top_skills})")
        
        if title_match["title_match_score"] >= 0.7:
            strengths.append(f"Direct job title match ('{title_match['best_matched_title']}')")
        elif title_match["title_match_score"] >= 0.35:
            strengths.append(f"Related past experience as '{title_match['best_matched_title']}'")

        if exp_match["experience_match_score"] >= 1.0:
            strengths.append(f"Tenure meets requirements ({exp_match['candidate_years']} yrs)")
        elif exp_match["is_uncertain"]:
            gaps.append("Experience tenure duration uncertain from text")
        else:
            gaps.append(f"Experience below requested ({exp_match['candidate_years']} yrs vs {exp_match['required_years']} yrs)")

        if edu_match["education_match_score"] >= 1.0:
            strengths.append(f"Education aligned ({edu_match['candidate_degree']} in {edu_match['candidate_discipline']})")
        else:
            gaps.append(edu_match["status"])

        if skill_match["missing_required"]:
            missing_str = ", ".join(skill_match["missing_required"][:3])
            gaps.append(f"Missing core requirements: {missing_str}")

        strength_txt = " • ".join(strengths) if strengths else "Moderate general keyword alignment."
        gap_txt = " • ".join(gaps) if gaps else "No critical qualification gaps identified."

        return f"Overall Screening Score: {composite_pct}% (TF-IDF Match: {tfidf_pct}%). Key Strengths: {strength_txt}. Areas for Review: {gap_txt}"
