"""
Comprehensive Evaluation & Adversarial Benchmarking Suite
AI Resume Screening & Candidate Ranking System (RankCraft AI)

Computes Information Retrieval metrics (P@K, MAP, MRR, NDCG@K) on standard dataset
and runs in-depth adversarial evaluations across 8 challenging candidate profiles.
"""

import os
import sys
import json
import csv
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ["MPLCONFIGDIR"] = os.path.join(BASE_DIR, ".matplotlib_cache")
os.makedirs(os.path.join(BASE_DIR, ".matplotlib_cache"), exist_ok=True)

import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = os.path.join(BASE_DIR, "data")
RESUMES_DIR = os.path.join(DATA_DIR, "resumes")
JD_DIR = os.path.join(DATA_DIR, "job_descriptions")
EVAL_DIR = os.path.join(DATA_DIR, "evaluation")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

from backend.resume_parser import parse_resume
from backend.ranking import ResumeRanker
from backend.skill_extractor import skill_extractor
from backend.preprocessing import preprocess_text


def compute_ndcg_at_k(actual_grades: list, k: int = 5) -> float:
    """Computes Normalized Discounted Cumulative Gain at K (NDCG@K)."""
    actual = np.array(actual_grades[:k], dtype=float)
    if len(actual) == 0 or np.sum(actual) == 0:
        return 0.0

    # DCG = sum((2^rel - 1) / log2(i + 2))
    gains = 2 ** actual - 1
    discounts = np.log2(np.arange(len(actual)) + 2)
    dcg = np.sum(gains / discounts)

    # Ideal DCG (IDCG)
    ideal = np.sort(actual_grades)[::-1][:k]
    ideal_gains = 2 ** ideal - 1
    ideal_discounts = np.log2(np.arange(len(ideal)) + 2)
    idcg = np.sum(ideal_gains / ideal_discounts)

    return float(dcg / idcg) if idcg > 0 else 0.0


def compute_average_precision(binary_relevance: list) -> float:
    """Computes Average Precision (AP) for a single ranked list."""
    relevant_count = 0
    precision_sum = 0.0
    for i, rel in enumerate(binary_relevance):
        if rel == 1:
            relevant_count += 1
            precision_sum += relevant_count / (i + 1)
    return precision_sum / relevant_count if relevant_count > 0 else 0.0


def compute_reciprocal_rank(binary_relevance: list) -> float:
    """Computes Reciprocal Rank (RR) - 1 / rank of first relevant item."""
    for i, rel in enumerate(binary_relevance):
        if rel == 1:
            return 1.0 / (i + 1)
    return 0.0


def run_standard_evaluation():
    print("=" * 70)
    print("1. RUNNING STANDARD 3-ROLE EVALUATION BENCHMARK")
    print("=" * 70)

    labels_path = os.path.join(EVAL_DIR, "relevance_labels.csv")
    if not os.path.exists(labels_path):
        raise FileNotFoundError(f"Relevance labels not found at {labels_path}")
    
    df_labels = pd.read_csv(labels_path)

    # Parse all Resumes
    resume_files = sorted([f for f in os.listdir(RESUMES_DIR) if not f.startswith(".")])
    parsed_resumes = []
    
    for fname in resume_files:
        ext = os.path.splitext(fname)[1].lower()
        if ext in [".pdf", ".docx", ".txt"]:
            fpath = os.path.join(RESUMES_DIR, fname)
            parsed = parse_resume(fpath, fname)
            cand_num = fname.split("_")[1] if "_" in fname else "01"
            cand_id = f"CAND-{int(cand_num):03d}" if cand_num.isdigit() else "CAND-001"
            parsed["candidate_id"] = cand_id
            parsed_resumes.append(parsed)

    ranker = ResumeRanker()
    evaluation_records = []
    all_candidate_rankings = []

    # Map job description files to job IDs
    jd_map = {
        "JOB-01": "job_01_senior_ai_ml_engineer.txt",
        "JOB-02": "job_02_fullstack_python_developer.txt",
        "JOB-03": "job_03_data_analyst.txt"
    }

    for job_id, jd_filename in jd_map.items():
        jd_path = os.path.join(JD_DIR, jd_filename)
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        job_title = jd_text.splitlines()[0].replace("Job Title:", "").strip()
        ranked_candidates = ranker.rank_candidates(jd_text, parsed_resumes)

        # Merge with Ground Truth Labels
        jd_labels = df_labels[df_labels["job_id"] == job_id].set_index("candidate_id")

        ordered_grades = []
        ordered_binary = []

        for cand in ranked_candidates:
            cid = cand["candidate_id"]
            label_row = jd_labels.loc[cid] if cid in jd_labels.index else None
            grade = int(label_row["grade"]) if label_row is not None else 0
            binary_rel = int(label_row["is_relevant"]) if label_row is not None else 0
            rationale = label_row["rationale"] if label_row is not None else "Unknown"

            cand["job_id"] = job_id
            cand["job_title"] = job_title
            cand["ground_truth_grade"] = grade
            cand["ground_truth_category"] = rationale
            cand["is_relevant_binary"] = binary_rel

            ordered_grades.append(grade)
            ordered_binary.append(binary_rel)
            all_candidate_rankings.append(cand)

        # Calculate Metrics
        total_eval = len(ranked_candidates)
        total_relevant = sum(ordered_binary)
        p1 = sum(ordered_binary[:1]) / 1.0
        p3 = sum(ordered_binary[:3]) / 3.0
        p5 = sum(ordered_binary[:5]) / 5.0
        recall_at_5 = sum(ordered_binary[:5]) / max(1, total_relevant)
        ap = compute_average_precision(ordered_binary)
        rr = compute_reciprocal_rank(ordered_binary)
        ndcg3 = compute_ndcg_at_k(ordered_grades, k=3)
        ndcg5 = compute_ndcg_at_k(ordered_grades, k=5)

        evaluation_records.append({
            "job_id": job_id,
            "job_title": job_title,
            "total_candidates": total_eval,
            "total_relevant": total_relevant,
            "precision_at_1": round(p1, 4),
            "precision_at_3": round(p3, 4),
            "precision_at_5": round(p5, 4),
            "recall_at_5": round(recall_at_5, 4),
            "map": round(ap, 4),
            "mrr": round(rr, 4),
            "ndcg_at_3": round(ndcg3, 4),
            "ndcg_at_5": round(ndcg5, 4)
        })

    df_eval = pd.DataFrame(evaluation_records)
    
    # Compute Macro Average
    macro_avg = {
        "job_id": "OVERALL",
        "job_title": "System Macro-Average",
        "total_candidates": int(df_eval["total_candidates"].mean()),
        "total_relevant": int(df_eval["total_relevant"].sum()),
        "precision_at_1": round(df_eval["precision_at_1"].mean(), 4),
        "precision_at_3": round(df_eval["precision_at_3"].mean(), 4),
        "precision_at_5": round(df_eval["precision_at_5"].mean(), 4),
        "recall_at_5": round(df_eval["recall_at_5"].mean(), 4),
        "map": round(df_eval["map"].mean(), 4),
        "mrr": round(df_eval["mrr"].mean(), 4),
        "ndcg_at_3": round(df_eval["ndcg_at_3"].mean(), 4),
        "ndcg_at_5": round(df_eval["ndcg_at_5"].mean(), 4)
    }
    df_eval = pd.concat([df_eval, pd.DataFrame([macro_avg])], ignore_index=True)
    df_eval.to_csv(os.path.join(RESULTS_DIR, "evaluation_results.csv"), index=False)
    print(df_eval.to_string(index=False))

    # Save Candidate Rankings CSV
    df_rankings = pd.DataFrame(all_candidate_rankings)
    df_rankings_export = df_rankings[[
        "job_id", "job_title", "rank", "candidate_id", "candidate_name", "file_type",
        "screening_score", "score_percentage", "skill_coverage_pct", "title_match_pct",
        "experience_match_pct", "education_match_pct", "ground_truth_grade", "ground_truth_category"
    ]]
    df_rankings_export.to_csv(os.path.join(RESULTS_DIR, "candidate_rankings.csv"), index=False)

    return df_eval, df_rankings


def run_adversarial_evaluation():
    print("\n" + "=" * 70)
    print("2. RUNNING ADVERSARIAL & CHALLENGING SCENARIOS BENCHMARK (8 CASES)")
    print("=" * 70)

    adv_path = os.path.join(EVAL_DIR, "adversarial_cases.json")
    with open(adv_path, "r", encoding="utf-8") as f:
        adv_data = json.load(f)

    benchmark_job = adv_data["benchmark_job"]
    cases = adv_data["cases"]

    # Load target Job Description
    jd_path = os.path.join(JD_DIR, "job_01_senior_ai_ml_engineer.txt")
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    # Format cases for ranking
    resumes_data = []
    for c in cases:
        resumes_data.append({
            "candidate_id": c["case_id"],
            "candidate_name": f"{c['candidate_name']} ({c['scenario']})",
            "file_name": f"{c['case_id'].lower()}.txt",
            "file_type": "TXT",
            "raw_text": c["raw_text"]
        })

    ranker = ResumeRanker()
    ranked_candidates = ranker.rank_candidates(jd_text, resumes_data)

    results_table = []
    for r in ranked_candidates:
        case_info = next(c for c in cases if c["case_id"] == r["candidate_id"])
        results_table.append({
            "Case ID": r["candidate_id"],
            "Scenario": case_info["scenario"],
            "Candidate Name": case_info["candidate_name"],
            "Ground Truth Grade": case_info["ground_truth_grade"],
            "Final Rank": r["rank"],
            "Screening Score (%)": r["screening_score"],
            "TF-IDF Match (%)": r["score_percentage"],
            "Skill Coverage (%)": r["skill_coverage_pct"],
            "Title Match (%)": r["title_match_pct"],
            "Experience Match (%)": r["experience_match_pct"],
            "Education Match (%)": r["education_match_pct"],
            "ATS Parseability (%)": r["ats_parseability"]["parseability_score"],
            "Why Ranked / Diagnostic": r["explainability"]
        })

    df_adv = pd.DataFrame(results_table)
    adv_csv_path = os.path.join(RESULTS_DIR, "adversarial_evaluation_results.csv")
    df_adv.to_csv(adv_csv_path, index=False)
    print(df_adv[["Case ID", "Scenario", "Final Rank", "Screening Score (%)", "TF-IDF Match (%)", "Skill Coverage (%)", "Experience Match (%)"]].to_string(index=False))

    return df_adv


def generate_diagnostic_plots(df_rankings, df_adv):
    print("\n" + "=" * 70)
    print("3. GENERATING PUBLICATION-READY DIAGNOSTIC FIGURES")
    print("=" * 70)
    sns.set_theme(style="whitegrid", palette="deep")

    # Plot 1: Score Distribution across Relevance Grades
    plt.figure(figsize=(9, 5.5))
    grade_labels = {3: "Grade 3\n(Highly Relevant)", 2: "Grade 2\n(Partially Relevant)", 1: "Grade 1\n(Weakly Relevant)", 0: "Grade 0\n(Irrelevant)"}
    df_plot = df_rankings.copy()
    df_plot["Grade Label"] = df_plot["ground_truth_grade"].map(grade_labels)

    sns.boxplot(
        x="Grade Label",
        y="screening_score",
        data=df_plot,
        order=["Grade 3\n(Highly Relevant)", "Grade 2\n(Partially Relevant)", "Grade 1\n(Weakly Relevant)", "Grade 0\n(Irrelevant)"],
        palette=["#10b981", "#3b82f6", "#f59e0b", "#ef4444"],
        width=0.45
    )
    sns.stripplot(
        x="Grade Label",
        y="screening_score",
        data=df_plot,
        order=["Grade 3\n(Highly Relevant)", "Grade 2\n(Partially Relevant)", "Grade 1\n(Weakly Relevant)", "Grade 0\n(Irrelevant)"],
        color="black",
        alpha=0.6,
        size=6,
        jitter=0.15
    )
    plt.title("Screening Score Distribution across Human Relevance Grades", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Ground Truth Relevance Tier", fontsize=11, fontweight="600")
    plt.ylabel("Composite Screening Score (%)", fontsize=11, fontweight="600")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "score_distribution.png"), dpi=300)
    plt.close()
    print("Saved: results/score_distribution.png")

    # Plot 2: Adversarial Cases Diagnostic Comparison (Pure TF-IDF vs Screening Score)
    plt.figure(figsize=(11, 6))
    df_adv_plot = df_adv.copy()
    df_adv_plot = df_adv_plot.sort_values(by="Screening Score (%)", ascending=False)

    x = np.arange(len(df_adv_plot))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))
    rects1 = ax.bar(x - width/2, df_adv_plot["Screening Score (%)"], width, label="Screening Score (Multi-Factor)", color="#6366f1")
    rects2 = ax.bar(x + width/2, df_adv_plot["TF-IDF Match (%)"], width, label="Pure TF-IDF Match", color="#94a3b8")

    ax.set_ylabel("Score Percentage (%)", fontsize=11, fontweight="600")
    ax.set_title("Adversarial Benchmark: Multi-Factor Screening Score vs Pure TF-IDF", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{row['Case ID']}\n{row['Scenario'][:16]}..." for _, row in df_adv_plot.iterrows()], fontsize=9, rotation=20)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "adversarial_comparison.png"), dpi=300)
    plt.close()
    print("Saved: results/adversarial_comparison.png")


if __name__ == "__main__":
    df_eval, df_rankings = run_standard_evaluation()
    df_adv = run_adversarial_evaluation()
    generate_diagnostic_plots(df_rankings, df_adv)
    print("\nEvaluation pipeline successfully completed!")
