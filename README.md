# RankCraft AI: Multi-Factor ATS Resume Screening & Candidate Ranking System

> **LaunchED Artificial Intelligence Major Capstone Project — Option 2**  
> An explainable, deterministic, multi-factor ATS candidate ranking engine combining TF-IDF Vectorization and Cosine Similarity with structured profile parsing, skill taxonomy normalization, experience/education alignment, and an 8-point ATS parseability check.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0%2B-green.svg)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6%2B-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Machine Learning & Multi-Factor Scoring Methodology](#machine-learning--multi-factor-scoring-methodology)
  - [1. Domain-Aware Text Ingestion & PII Sanitization](#1-domain-aware-text-ingestion--pii-sanitization)
  - [2. Configurable Skill Taxonomy Normalization](#2-configurable-skill-taxonomy-normalization)
  - [3. Sublinear TF-IDF & Cosine Similarity (Required Baseline)](#3-sublinear-tf-idf--cosine-similarity-required-baseline)
  - [4. Composite Screening Score Formula](#4-composite-screening-score-formula)
  - [5. 8-Point ATS Parseability Audit](#5-8-point-ats-parseability-audit)
- [Project Structure](#project-structure)
- [Installation & Quickstart](#installation--quickstart)
- [Running the Web Dashboard & FastAPI Backend](#running-the-web-dashboard--fastapi-backend)
- [Running the Jupyter Notebook](#running-the-jupyter-notebook)
- [Running Automated Tests](#running-automated-tests)
- [Evaluation & Benchmark Results](#evaluation--benchmark-results)
  - [Standard 3-Role IR Benchmark](#standard-3-role-ir-benchmark)
  - [Adversarial Benchmark Case Studies (8 Scenarios)](#adversarial-benchmark-case-studies-8-scenarios)
- [Privacy & Ethical Guardrails](#privacy--ethical-guardrails)
- [Limitations & Future Scope](#limitations--future-scope)

---

## 🎯 Overview

**RankCraft AI** is an explainable candidate screening prototype built for talent acquisition teams. It allows recruiters to evaluate multiple resumes in diverse formats (**PDF**, **DOCX**, **TXT**) against job descriptions.

The system combines statistical Information Retrieval (**TF-IDF + Cosine Similarity**) with deterministic rule-based candidate profiling: extracting canonical skills (`JS` $\rightarrow$ `JavaScript`, `K8s` $\rightarrow$ `Kubernetes`), verifying required vs preferred qualifications, matching past job titles and experience duration, checking education degree levels, and auditing resume formatting via an **8-point ATS Parseability Checker**.

---

## ✨ Key Features

- 📄 **Multi-Format Ingestion:** Robust text extraction for `.pdf` (via `pypdf`), `.docx` (via `python-docx`), and `.txt` files.
- 🛡️ **Domain-Aware NLP Preprocessing:** Strips PII (email, phone, URLs) while explicitly preserving compound technical terms (`C++`, `.NET`, `CI/CD`, `Scikit-Learn`, `FastAPI`).
- 🏷️ **Configurable Skill Normalization:** External JSON taxonomy mapping aliases and abbreviations to canonical skills (`data/config/skills_taxonomy.json`).
- 📌 **Required vs. Preferred Classification:** Automatically parses job descriptions to distinguish mandatory vs nice-to-have qualifications.
- 📐 **Sublinear TF-IDF + Cosine Similarity:** Primary required statistical vector space model.
- ⚖️ **Project-Defined Composite Screening Score:** Transparent weighted evaluation across 5 dimensions:
  $$\text{Screening Score} = 0.40 \times \text{TF-IDF} + 0.25 \times \text{Skills} + 0.15 \times \text{Title} + 0.10 \times \text{Experience} + 0.10 \times \text{Education}$$
- 🔍 **8-Point ATS Parseability Diagnostic:** Checks extraction completeness, contact detection, timeline validity, and section headers (Score: 0-100%).
- 📊 **Candidate Comparison Matrix:** Side-by-side comparison modal in the UI.
- 📥 **1-Click CSV Export:** Downloads candidate rankings, scores, and explainability breakdowns.
- 💡 **Explainability Engine:** Generates natural language narratives detailing why each candidate ranked at their position.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Recruiter / User UI                      │
│            (HTML5 / CSS3 / Vanilla JS Web Dashboard)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP Multipart / REST Form
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend API                     │
│    - /rank  - /rank-raw-text  - /api/sample-data  - /export  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Ingestion & Structured Parsing Layer          │
│   - pypdf (PDF)  - python-docx (DOCX)  - txt decoder        │
│   - Structured Parser (Contact, Experience, Degree, ATS)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Skill Extraction & Taxonomy Normalization       │
│     - Configurable JSON Taxonomy (Synonyms & Abbreviations) │
│     - Required vs Preferred JD Qualification Segmentation   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              ML Vectorization & Multi-Factor Matching       │
│   - Scikit-Learn TfidfVectorizer (Unigrams & Bigrams)       │
│   - Cosine Similarity Dot Product                           │
│   - Multi-Factor Matchers (Title, Experience, Education)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Output & Explainability Engine              │
│  Rank #1..N, Screening Score, TF-IDF Match %, Matched Skills│
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Machine Learning & Multi-Factor Scoring Methodology

### 1. Domain-Aware Text Ingestion & PII Sanitization
Compound programming terms are normalized before punctuation stripping:
- `C++` $\rightarrow$ `cpp`, `C#` $\rightarrow$ `csharp`, `.NET` $\rightarrow$ `dotnet`, `Node.js` $\rightarrow$ `nodejs`, `CI/CD` $\rightarrow$ `cicd`, `Scikit-Learn` $\rightarrow$ `scikitlearn`, `FastAPI` $\rightarrow$ `fastapi`.

### 2. Configurable Skill Taxonomy Normalization
An external JSON taxonomy (`data/config/skills_taxonomy.json`) deterministically maps abbreviations (`ML`, `NLP`, `DL`, `K8s`, `Postgres`, `TS`, `JS`) to standardized canonical names.

### 3. Sublinear TF-IDF & Cosine Similarity (Required Baseline)
Transformed into a shared feature space using logarithmic term frequency and smoothed inverse document frequency:
$$\text{TF-IDF}(t, d, D) = (1 + \log(\text{TF}(t, d))) \times \left(\log\left(\frac{1 + |D|}{1 + \text{DF}(t)}\right) + 1\right)$$
$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \cos(\theta) = \mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^M u_i v_i$$

### 4. Composite Screening Score Formula
A transparent, project-defined composite metric combining:
- **TF-IDF Match ($40\%$):** Directional cosine similarity.
- **Skill Coverage ($25\%$):** Weighted overlap with Required ($80\%$) and Preferred ($20\%$) skills.
- **Job Title Match ($15\%$):** Role title token overlap and core noun matching.
- **Experience Match ($10\%$):** Ratio of candidate extracted years to JD requirement (uncertainty handled explicitly).
- **Education Match ($10\%$):** Degree level hierarchy (PhD > Master's > Bachelor's) and technical discipline alignment.

### 5. 8-Point ATS Parseability Audit
1. Text Extraction Cleanliness ($\ge 50$ words)
2. Candidate Name Detection
3. Email Contact Detection
4. Phone Contact Detection
5. Work Experience Section
6. Timeline / Dates Extraction
7. Education & Degree Detection
8. Technical Skill Extraction ($\ge 4$ skills)

---

## 📁 Project Structure

```
resume-screening-ai/
│
├── data/
│   ├── config/
│   │   └── skills_taxonomy.json      # Configurable skill normalization dictionary
│   ├── resumes/                      # 12 Sample resumes (.pdf, .docx, .txt)
│   ├── job_descriptions/             # 3 Target job description files (.txt)
│   ├── metadata/                     # Candidate metadata CSV
│   └── evaluation/
│       ├── relevance_labels.csv      # 36 Ground-truth relevance labels CSV
│       └── adversarial_cases.json    # 8 Adversarial stress-test cases JSON
│
├── notebooks/
│   └── Resume_Screening_Analysis.ipynb  # Executed 16-section demonstration notebook
│
├── backend/
│   ├── __init__.py
│   ├── main.py                       # FastAPI REST backend & static file server
│   ├── ranking.py                    # TF-IDF & Multi-Factor ranking engine
│   ├── preprocessing.py              # Domain-aware NLP cleaning & token mapping
│   ├── resume_parser.py              # Multi-format document parser (PDF, DOCX, TXT)
│   ├── structured_parser.py          # Structured profile & ATS parseability auditor
│   ├── skill_extractor.py            # Configurable skill taxonomy extractor
│   └── matcher.py                    # Title, Experience & Education matchers
│
├── frontend/
│   ├── index.html                    # Responsive ATS web dashboard
│   ├── style.css                     # Modern stylesheet with modal & comparison styles
│   └── script.js                     # Client controller (ranking, modals, export)
│
├── results/
│   ├── candidate_rankings.csv        # Detailed candidate rankings output
│   ├── evaluation_results.csv        # IR benchmark metrics (P@K, MAP, NDCG)
│   ├── adversarial_evaluation_results.csv # 8 Adversarial case benchmark results
│   ├── score_distribution.png        # Score boxplot across relevance grades
│   ├── adversarial_comparison.png    # TF-IDF vs Screening score diagnostic chart
│   └── architecture_diagram.png      # System architecture workflow diagram
│
├── report/
│   └── Final_Analytical_Report.md    # 21-section comprehensive analytical report
│
├── demo/
│   └── demo_script.md                # 5-7 minute presentation script & templates
│
├── scripts/
│   ├── generate_sample_data.py       # Sample dataset generator script
│   ├── run_evaluation.py             # Evaluation & plotting execution script
│   └── build_and_execute_notebook.py # Notebook builder & preprocessor script
│
├── tests/
│   ├── test_preprocessing.py         # NLP cleaning tests
│   ├── test_parser.py                # Document parsing tests
│   ├── test_ranking.py               # TF-IDF & deterministic ranking tests
│   ├── test_ats_features.py          # ATS parsing, taxonomy, and matcher tests
│   ├── test_adversarial_qa.py        # Adversarial QA & API robustness tests
│   └── test_api.py                   # FastAPI REST integration tests
│
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
├── FINAL_SUBMISSION_CHECKLIST.md     # Capstone submission checklist
└── .gitignore
```

---

## 🚀 Installation & Quickstart

```bash
# 1. Clone repository & create virtual environment
git clone https://github.com/your-username/resume-screening-ai.git
cd resume-screening-ai

python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 🖥️ Running the Web Dashboard & FastAPI Backend

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- 🌐 **Web Dashboard:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📖 **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 🚀 **1-Click Demo:** Click "🚀 1-Click Instant Demo" in the top banner.

---

## 📓 Running the Jupyter Notebook

```bash
jupyter notebook notebooks/Resume_Screening_Analysis.ipynb
```

---

## 🧪 Running Automated Tests

```bash
pytest -v tests/
```
**Expected output:** `54 passed in ~1.3s` across all unit, parser, ATS, ranking, API, SaaS workflows, and security tests.

---

## 📈 Evaluation & Benchmark Results

### Standard 3-Role IR Benchmark
| Job Role ID | Role Title | Total Evaluated | Precision@1 | Precision@3 | Precision@5 | MAP | MRR | NDCG@5 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`JOB-01`** | Senior AI / ML Engineer | 12 | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **`JOB-02`** | Full-Stack Python Developer | 12 | **1.0000** | **1.0000** | **0.8000** | **0.9667** | **1.0000** | **0.9497** |
| **`JOB-03`** | Data Analyst & BI Specialist| 12 | **1.0000** | **1.0000** | **0.6000** | **0.9167** | **1.0000** | **0.9286** |
| **OVERALL** | **System Macro-Average** | **12** | **1.0000** | **1.0000** | **0.8000** | **0.9611** | **1.0000** | **0.9594** |

### Adversarial Benchmark Case Studies (8 Scenarios)
| Case ID | Scenario | Final Rank | Screening Score (%) | TF-IDF Match (%) | Diagnostic Result |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **`CASE-A`** | Exact Keyword Match | #1 | **44.4%** | 12.67% | Ideal baseline candidate meeting all requirements. |
| **`CASE-C`** | Abbreviation Match | #2 | **40.5%** | 8.02% | Skill normalizer resolves `ML`, `DL`, `K8s`, `CI/CD`. |
| **`CASE-G`** | Strong Exp. / No Degree | #3 | **36.8%** | 9.86% | Rewarded for 10y experience; degree gap transparently penalized. |
| **`CASE-B`** | Synonym Match | #4 | **34.8%** | 12.61% | Taxonomy maps `computational linguistics` & `containerization`. |
| **`CASE-D`** | Keyword Stuffer (Sales Dir.) | #5 | **31.9%** | 5.77% | **Corrected:** Pure TF-IDF gets tricked; Title/Degree matchers penalize to Rank #5. |
| **`CASE-H`** | Junior (0.5y Exp.) | #6 | **31.4%** | 6.53% | Penalized appropriately on experience duration. |
| **`CASE-F`** | Missing Critical Skills | #7 | **30.3%** | 3.43% | Missing FastAPI/Docker flagged in skill coverage. |
| **`CASE-E`** | Descriptive Concept Wording| #8 | **24.9%** | 6.87% | Demonstrates lexical limits without dense embeddings. |

---

## 🛡️ Privacy & Ethical Guardrails

- **Demographic Scrubbing:** Ranking strictly ignores name, gender, age, email, phone, address, photo, nationality, and marital status.
- **Human-in-the-Loop:** System acts exclusively as a prioritization assistant. No automated hiring or rejection decisions are executed autonomously.

---

## 🔮 Limitations & Future Scope

- **Descriptive Text:** Candidates describing achievements conceptually without keywords receive lower lexical scores (future scope: hybrid Sentence-BERT reranking).
- **Image-Only Resumes:** Rasterized image PDFs require OCR (future scope: Tesseract integration).

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
