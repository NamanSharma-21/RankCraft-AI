"""
Skill Extraction & Normalization Module
Provides deterministic, dictionary-based skill extraction, canonical normalization,
and section-aware required vs. preferred skill classification.
"""

import json
import os
import re
from typing import List, Dict, Any, Set, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY_PATH = os.path.join(BASE_DIR, "data", "config", "skills_taxonomy.json")

# Default fallback taxonomy in case JSON file is inaccessible
DEFAULT_TAXONOMY = {
    "Python": ["python", "python3", "py"],
    "Machine Learning": ["machine learning", "ml", "statistical learning"],
    "Deep Learning": ["deep learning", "dl", "neural networks"],
    "Natural Language Processing": ["natural language processing", "nlp", "computational linguistics", "text processing"],
    "Computer Vision": ["computer vision", "cv", "image processing"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "tf", "keras"],
    "Scikit-Learn": ["scikit-learn", "scikitlearn", "sklearn"],
    "TF-IDF": ["tf-idf", "tfidf"],
    "Transformers": ["transformers", "huggingface", "llms", "large language models", "bert", "gpt"],
    "MLOps": ["mlops", "model deployment", "model monitoring", "ml pipeline"],
    "FastAPI": ["fastapi", "fast api"],
    "Django": ["django", "django rest framework", "drf"],
    "Flask": ["flask"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs", "node"],
    "HTML5": ["html5", "html"],
    "CSS3": ["css3", "css"],
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "SQL": ["sql", "structured query language", "relational database", "relational databases"],
    "Docker": ["docker", "containerization", "containers"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "cicd", "ci cd", "continuous integration", "continuous deployment"],
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "GCP": ["gcp", "google cloud platform", "google cloud"],
    "Azure": ["azure", "microsoft azure"],
    "Git": ["git", "github", "gitlab", "version control"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Tableau": ["tableau"],
    "Power BI": ["power bi", "powerbi", "power-bi"],
    "Excel": ["excel", "advanced excel", "spreadsheets", "vba"],
    "ETL": ["etl", "extract transform load", "data pipelines", "data pipeline"],
    "Data Warehousing": ["data warehousing", "data warehouse", "snowflake", "bigquery", "redshift"],
    "Data Visualization": ["data visualization", "data storytelling", "bi reporting", "dashboards"],
    "REST API": ["rest api", "restful api", "restful apis", "rest apis", "rest"],
    "GraphQL": ["graphql"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp"],
    ".NET": [".net", "dotnet", "asp.net"],
    "Java": ["java"],
    "Go": ["golang", "go"],
    "Rust": ["rust"],
    "Pytest": ["pytest", "unit testing", "automated testing"],
    "Linux": ["linux", "unix", "bash", "shell scripting", "shell"],
    "Agile": ["agile", "scrum", "kanban"]
}


class SkillExtractor:
    """
    Deterministic, configurable skill extractor and normalizer.
    """

    def __init__(self, taxonomy_path: str = TAXONOMY_PATH):
        self.taxonomy: Dict[str, List[str]] = self._load_taxonomy(taxonomy_path)
        self.compiled_patterns: List[Tuple[str, re.Pattern]] = self._compile_patterns()

    def _load_taxonomy(self, path: str) -> Dict[str, List[str]]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("skills", DEFAULT_TAXONOMY)
            except Exception:
                return DEFAULT_TAXONOMY
        return DEFAULT_TAXONOMY

    def _compile_patterns(self) -> List[Tuple[str, re.Pattern]]:
        patterns = []
        for canonical, aliases in self.taxonomy.items():
            all_terms = [canonical] + aliases
            # Sort terms by length descending to match longer multi-word phrases first
            all_terms = sorted(list(set(all_terms)), key=len, reverse=True)
            
            regex_parts = []
            for term in all_terms:
                escaped = re.escape(term)
                # Word boundaries or non-word lookaround
                # Handle special ending chars like ++ or # or .net
                if term.endswith("+") or term.endswith("#"):
                    pattern_str = rf"(?<!\w){escaped}(?!\w)"
                elif term.startswith("."):
                    pattern_str = rf"(?<!\w){escaped}(?!\w)"
                else:
                    pattern_str = rf"\b{escaped}\b"
                regex_parts.append(pattern_str)

            combined_regex = re.compile("|".join(regex_parts), re.IGNORECASE)
            patterns.append((canonical, combined_regex))
        return patterns

    def extract_skills(self, text: str) -> List[str]:
        """
        Extracts a deduplicated list of canonical skill names found in text.
        """
        if not text or not text.strip():
            return []

        matched_skills = []
        for canonical, pattern in self.compiled_patterns:
            if pattern.search(text):
                matched_skills.append(canonical)
        return sorted(matched_skills)

    def extract_jd_skills(self, jd_text: str) -> Dict[str, Any]:
        """
        Extracts skills from a job description and segments them into
        required vs preferred skills based on section headings.
        """
        if not jd_text or not jd_text.strip():
            return {
                "all_skills": [],
                "required_skills": [],
                "preferred_skills": [],
                "classification_confidence": "uncertain",
                "classification_note": "Empty job description provided."
            }

        all_skills = self.extract_skills(jd_text)

        # Regex patterns for section headers
        req_pattern = re.compile(
            r"(?:requirements|required qualifications|minimum qualifications|must have|what you need|qualifications|what you'll need|responsibilities):?",
            re.IGNORECASE
        )
        pref_pattern = re.compile(
            r"(?:preferred qualifications|nice to have|bonus points|preferred skills|desired qualifications|good to have):?",
            re.IGNORECASE
        )

        lines = jd_text.splitlines()
        req_lines = []
        pref_lines = []
        current_section = "other"

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if pref_pattern.search(stripped) and len(stripped) < 60:
                current_section = "pref"
                continue
            elif req_pattern.search(stripped) and len(stripped) < 60:
                current_section = "req"
                continue
            elif stripped.endswith(":") and len(stripped) < 40:
                # Other unknown header
                current_section = "other"
                continue

            if current_section == "req":
                req_lines.append(stripped)
            elif current_section == "pref":
                pref_lines.append(stripped)

        req_text = "\n".join(req_lines)
        pref_text = "\n".join(pref_lines)

        req_skills = self.extract_skills(req_text)
        pref_skills = self.extract_skills(pref_text)

        # Determine confidence and handle overlap / missing sections
        if req_skills and pref_skills:
            confidence = "high"
            note = "Explicit 'Required' and 'Preferred' qualification sections identified."
            # Remove overlap from preferred if already required
            pref_skills = [s for s in pref_skills if s not in req_skills]
            # Any remaining skills in doc not categorized go to required
            uncat = [s for s in all_skills if s not in req_skills and s not in pref_skills]
            req_skills.extend(uncat)
        elif req_skills:
            confidence = "medium"
            note = "Required qualifications section identified; all extracted skills assigned as required."
            req_skills = all_skills
            pref_skills = []
        elif pref_skills:
            confidence = "medium"
            note = "Preferred qualifications section identified; remaining skills assigned as required."
            req_skills = [s for s in all_skills if s not in pref_skills]
        else:
            confidence = "uncertain"
            note = "No explicit section headers detected; skills classified as required with uncertainty."
            req_skills = all_skills
            pref_skills = []

        return {
            "all_skills": all_skills,
            "required_skills": sorted(req_skills),
            "preferred_skills": sorted(pref_skills),
            "classification_confidence": confidence,
            "classification_note": note
        }

    def match_skills(
        self,
        candidate_skills: List[str],
        jd_skills_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compares candidate extracted skills against JD skills profile.
        """
        cand_set = set(candidate_skills)
        all_jd_set = set(jd_skills_profile.get("all_skills", []))
        req_set = set(jd_skills_profile.get("required_skills", []))
        pref_set = set(jd_skills_profile.get("preferred_skills", []))

        matched_all = sorted(list(cand_set.intersection(all_jd_set)))
        matched_req = sorted(list(cand_set.intersection(req_set)))
        missing_req = sorted(list(req_set - cand_set))
        matched_pref = sorted(list(cand_set.intersection(pref_set)))
        missing_pref = sorted(list(pref_set - cand_set))

        # Calculate coverage score
        if req_set and pref_set:
            req_cov = len(matched_req) / len(req_set)
            pref_cov = len(matched_pref) / len(pref_set)
            # 80% weight on required, 20% on preferred
            coverage_score = (req_cov * 0.8) + (pref_cov * 0.2)
        elif req_set:
            coverage_score = len(matched_req) / len(req_set)
        elif all_jd_set:
            coverage_score = len(matched_all) / len(all_jd_set)
        else:
            coverage_score = 1.0 if not cand_set else 0.5

        coverage_score = max(0.0, min(1.0, coverage_score))

        return {
            "matched_skills": matched_all,
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref,
            "total_jd_skills_count": len(all_jd_set),
            "matched_skills_count": len(matched_all),
            "skill_coverage_ratio": round(coverage_score, 4),
            "skill_coverage_percentage": round(coverage_score * 100, 1),
            "classification_confidence": jd_skills_profile.get("classification_confidence", "uncertain")
        }


# Global singleton instance for easy import
skill_extractor = SkillExtractor()
