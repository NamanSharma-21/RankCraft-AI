# RankCraft-AI

# RankCraft AI

### Intelligent Recruiting Workspace & Multi-Factor Candidate Screening

RankCraft AI is an AI-assisted recruiting platform designed to help hiring teams screen and prioritize candidates more efficiently.

The system combines **TF-IDF text representation, cosine similarity, deterministic skill normalization, structured resume analysis, and multi-factor matching** to generate transparent candidate screening scores.

Rather than treating candidate screening as a black-box prediction, RankCraft AI exposes the signals contributing to each candidate's ranking, including skills, experience, education, job-title relevance, and resume parseability.

> **Important:** RankCraft AI is a screening and decision-support system. It does not make final hiring decisions.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [ML Pipeline](#ml-pipeline)
- [Screening Methodology](#screening-methodology)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Data](#data)
- [Resume Processing](#resume-processing)
- [API](#api)
- [Security](#security)
- [Testing](#testing)
- [Performance](#performance)
- [Running Locally](#running-locally)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Responsible AI](#responsible-ai)
- [Limitations](#limitations)
- [Research Context](#research-context)
- [Future Improvements](#future-improvements)
- [License](#license)

---

# Overview

Recruiters often need to review large numbers of resumes against a single job description.

Traditional resume screening can require substantial manual effort and may make it difficult to consistently compare candidates.

RankCraft AI addresses this workflow by transforming a job description and candidate resumes into structured screening signals.

### Core workflow

```text
                    JOB DESCRIPTION
                           │
                           ▼
                  Text Preprocessing
                           │
                           ▼
                    TF-IDF Vectorizer
                           │
                           │
RESUMES ───────► Text Preprocessing
                           │
                           ▼
                    TF-IDF Vectors
                           │
                           ▼
                 Cosine Similarity
                           │
                           ▼
              Multi-Factor Candidate
                    Evaluation
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Skills       Experience    Education
              │            │            │
              └────────────┼────────────┘
                           ▼
                  Screening Score
                           │
                           ▼
                  Candidate Ranking
                           │
                           ▼
              Recruiter Review & Action



# Reframed Question

You need a **GitHub-ready README for RankCraft AI** that accurately represents the current implementation, architecture, ML methodology, dataset handling, testing, and deployment, while looking professional enough for a public project repository.

I’ve based this on the deployment/audit document you uploaded, rather than inventing capabilities. 

Below is a **copy-paste-ready `README.md`**.

````markdown
# RankCraft AI

### Intelligent Recruiting Workspace & Multi-Factor Candidate Screening

RankCraft AI is an AI-assisted recruiting platform designed to help hiring teams screen and prioritize candidates more efficiently.

The system combines **TF-IDF text representation, cosine similarity, deterministic skill normalization, structured resume analysis, and multi-factor matching** to generate transparent candidate screening scores.

Rather than treating candidate screening as a black-box prediction, RankCraft AI exposes the signals contributing to each candidate's ranking, including skills, experience, education, job-title relevance, and resume parseability.

> **Important:** RankCraft AI is a screening and decision-support system. It does not make final hiring decisions.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [ML Pipeline](#ml-pipeline)
- [Screening Methodology](#screening-methodology)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Data](#data)
- [Resume Processing](#resume-processing)
- [API](#api)
- [Security](#security)
- [Testing](#testing)
- [Performance](#performance)
- [Running Locally](#running-locally)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Responsible AI](#responsible-ai)
- [Limitations](#limitations)
- [Research Context](#research-context)
- [Future Improvements](#future-improvements)
- [License](#license)

---

# Overview

Recruiters often need to review large numbers of resumes against a single job description.

Traditional resume screening can require substantial manual effort and may make it difficult to consistently compare candidates.

RankCraft AI addresses this workflow by transforming a job description and candidate resumes into structured screening signals.

### Core workflow

```text
                    JOB DESCRIPTION
                           │
                           ▼
                  Text Preprocessing
                           │
                           ▼
                    TF-IDF Vectorizer
                           │
                           │
RESUMES ───────► Text Preprocessing
                           │
                           ▼
                    TF-IDF Vectors
                           │
                           ▼
                 Cosine Similarity
                           │
                           ▼
              Multi-Factor Candidate
                    Evaluation
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Skills       Experience    Education
              │            │            │
              └────────────┼────────────┘
                           ▼
                  Screening Score
                           │
                           ▼
                  Candidate Ranking
                           │
                           ▼
              Recruiter Review & Action
````

The objective is not to replace recruiters.

The objective is to reduce repetitive screening work while making the evidence behind candidate rankings visible.

---

# Key Features

## AI-Assisted Resume Screening

Compare candidate resumes against a target job description using TF-IDF vectorization and cosine similarity.

## Multi-Factor Candidate Matching

Candidate evaluation incorporates multiple structured signals:

* TF-IDF relevance
* Skill coverage
* Job-title relevance
* Experience duration
* Education level
* ATS parseability

## Explainable Screening

Instead of presenting only a single opaque score, RankCraft AI exposes the signals contributing to the screening result.

Examples include:

* Matched skills
* Missing skills
* Experience match
* Education match
* Job-title match
* TF-IDF relevance
* Resume parseability

## Candidate Ranking

Candidates can be ranked according to calculated screening results, allowing recruiters to prioritize review.

## Resume Parsing

The system supports extraction from:

* PDF
* DOCX
* TXT

## Skill Normalization

A configurable skill taxonomy normalizes common aliases and technology terms into canonical skills.

For example, multiple representations of the same technology can be mapped to a consistent internal representation.

## ATS-Oriented Resume Diagnostics

The system includes an 8-point parseability diagnostic to identify structural characteristics that may affect automated resume processing.

## Recruiting Workspace

The application provides a SaaS-style workflow around:

* Jobs
* Candidates
* Screening
* Candidate pipeline
* Analytics
* Workspace activity
* Authentication

## Candidate Pipeline

Candidates can move through recruiting stages such as:

```text
Applied
   ↓
Screening
   ↓
Shortlisted
   ↓
Interview
   ↓
Offer
   ↓
Hired
```

---

# How It Works

RankCraft AI follows a deterministic processing pipeline.

### 1. Job Description

The recruiter provides a target job description containing information such as:

* role
* required skills
* preferred skills
* experience requirements
* education requirements
* responsibilities

### 2. Resume Ingestion

Candidate resumes are uploaded through the application.

The system supports PDF, DOCX, and TXT documents.

### 3. Text Extraction

Resume content is extracted into text using the appropriate parser.

### 4. Preprocessing

The extracted text passes through domain-aware preprocessing.

This includes:

* normalization
* text cleaning
* preservation of compound technology terms
* PII-oriented processing
* token preparation

### 5. Skill Extraction

A deterministic skill taxonomy identifies and normalizes recognized technologies and skills.

### 6. TF-IDF Representation

The job description and resumes are transformed into TF-IDF vectors.

Both unigrams and bigrams are used.

### 7. Cosine Similarity

Cosine similarity measures the textual relevance between the job description and each candidate resume.

### 8. Structured Matching

Additional deterministic matchers evaluate:

* job title
* experience tenure
* education degree level
* ATS parseability

### 9. Screening Score

The system combines the available screening signals into a candidate screening result.

### 10. Ranking

Candidates are ordered according to their calculated screening results.

### 11. Recruiter Review

The recruiter can inspect the underlying evidence and decide what action to take.

---

# ML Pipeline

The core machine-learning/NLP pipeline is intentionally deterministic and interpretable.

```text
Resume / Job Description
          │
          ▼
    Text Extraction
          │
          ▼
     Preprocessing
          │
          ▼
    Skill Extraction
          │
          ▼
    TF-IDF Vectorization
          │
          ▼
   Cosine Similarity
          │
          ▼
 Structured Matchers
          │
     ┌────┼─────┐
     ▼    ▼     ▼
   Title Experience Education
          │
          ▼
   ATS Parseability
          │
          ▼
   Screening Score
          │
          ▼
 Candidate Ranking
```

## TF-IDF

Term Frequency-Inverse Document Frequency represents text according to the importance of its terms.

The implementation uses:

* unigrams
* bigrams
* scikit-learn `TfidfVectorizer`

This allows the system to represent both individual terms and multi-word technical expressions.

## Cosine Similarity

Cosine similarity measures the angular similarity between the job-description vector and resume vector.

Conceptually:

```text
                 A · B
cosine(A,B) = ───────────
              ||A|| ||B||
```

A higher similarity indicates greater textual overlap between the candidate resume and target job description.

---

# Screening Methodology

RankCraft AI separates textual relevance from structured candidate signals.

### Primary signals

| Signal           | Purpose                                           |
| ---------------- | ------------------------------------------------- |
| TF-IDF Relevance | Measures textual similarity between JD and resume |
| Skill Coverage   | Measures recognized skill alignment               |
| Experience Match | Evaluates experience tenure                       |
| Education Match  | Evaluates degree-level requirements               |
| Job Title Match  | Evaluates title relevance                         |
| ATS Parseability | Evaluates structural resume characteristics       |

The result is presented as a **Screening Score** rather than a hiring probability.

The system is designed to support recruiter judgment rather than make autonomous hiring decisions.

---

# System Architecture

RankCraft AI currently uses a lightweight full-stack architecture.

```text
┌────────────────────────────────────────────┐
│                 Frontend                   │
│                                            │
│ HTML5 + CSS3 + ES6 JavaScript              │
│ Single Page Application                    │
└─────────────────────┬──────────────────────┘
                      │
                      │ HTTP
                      ▼
┌────────────────────────────────────────────┐
│                  FastAPI                   │
│                                            │
│ REST API                                   │
│ Authentication                             │
│ Candidate Management                       │
│ Job Management                             │
│ Screening Endpoints                        │
└─────────────────────┬──────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────┐
│               ML / NLP Layer               │
│                                            │
│ Resume Parser                              │
│ Preprocessing                              │
│ Skill Extraction                           │
│ TF-IDF                                     │
│ Cosine Similarity                          │
│ Structured Matchers                        │
└─────────────────────┬──────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────┐
│                 Data Layer                 │
│                                            │
│ Static datasets                            │
│ Skill taxonomy                             │
│ Sample resumes                             │
│ Job descriptions                           │
│ Evaluation data                            │
└────────────────────────────────────────────┘
```

---

# Technology Stack

## Frontend

* HTML5
* Modern CSS3
* JavaScript ES6+
* Single Page Application architecture

The frontend intentionally has **zero build-step requirements**.

There is no dependency on:

* React
* Vue
* Next.js
* Vite
* Webpack
* Node.js

for the current frontend implementation.

## Backend

* Python 3.9+
* FastAPI
* Uvicorn

## Machine Learning / NLP

* scikit-learn
* NumPy
* TF-IDF
* Cosine similarity
* Deterministic skill taxonomy

## Document Processing

* pypdf
* python-docx
* standard TXT decoding

## Testing

* pytest

---

# Project Structure

```text
ai-resume-screening-platform/
│
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── vercel.json
├── requirements.txt
├── README.md
├── DESIGN.md
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── ranking.py
│   ├── preprocessing.py
│   ├── resume_parser.py
│   ├── structured_parser.py
│   ├── skill_extractor.py
│   └── matcher.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── data/
│   ├── config/
│   │   └── skills_taxonomy.json
│   │
│   ├── job_descriptions/
│   │
│   ├── resumes/
│   │
│   ├── metadata/
│   │
│   └── evaluation/
│
└── tests/
    ├── test_api.py
    ├── test_saas_features.py
    ├── test_ats_features.py
    ├── test_adversarial_qa.py
    ├── test_ranking.py
    ├── test_parser.py
    └── test_preprocessing.py
```

---

# Data

The repository contains demonstration and evaluation data required to reproduce the application workflow.

## Data categories

### Skill Taxonomy

```text
data/config/skills_taxonomy.json
```

Contains canonical skill names and aliases used for deterministic normalization.

### Job Descriptions

```text
data/job_descriptions/
```

Contains sample target job descriptions.

### Sample Resumes

```text
data/resumes/
```

Contains pre-packaged demonstration resumes.

### Metadata

```text
data/metadata/
```

Contains candidate metadata used by the application.

### Evaluation Data

```text
data/evaluation/
```

Contains relevance labels and adversarial evaluation cases.

---

# Privacy and Data Handling

Custom resume uploads are processed **in memory**.

Uploaded files are read into Python memory, parsed, and converted into structured information.

Custom uploaded resumes are not intentionally written to persistent local storage by the application.

The current implementation does not use an external SQL or NoSQL database.

Application workspace state is maintained in memory.

This architecture is appropriate for a prototype/demo environment but has important implications for production deployment, described below.

> Do not upload real patient, hospital, or otherwise sensitive personal data to this public repository.

The repository should contain only synthetic, demonstration, or appropriately de-identified data.

---

# API

The backend exposes REST endpoints for the application workflow.

Core endpoint categories include:

### Health

```text
GET /health
```

Used to verify backend availability.

### Resume Ranking

```text
POST /rank
POST /rank-raw-text
```

Used to calculate candidate relevance against a target job description.

### Sample Dataset Ranking

```text
POST /api/rank-sample-data
```

Runs the ranking pipeline against the bundled demonstration dataset.

### Jobs

```text
POST /api/jobs
```

Creates a job.

### Candidate Pipeline

```text
PATCH /api/candidates/{id}/stage
```

Updates a candidate's recruiting stage.

### CSV Export

```text
GET /api/export-csv
```

Exports supported screening data.

### API Documentation

FastAPI provides interactive API documentation during development.

```text
/docs
```

---

# Security

Security has been considered as part of the application architecture.

Implemented protections include:

* upload size limits
* batch size limits
* path traversal protection
* input validation
* controlled file handling
* production environment configuration
* CORS configuration
* protected application routes
* security-oriented automated tests

## Upload Limits

Default configuration:

```text
Maximum file size: 10 MB
Maximum resumes per batch: 50
```

These limits help prevent uncontrolled memory consumption during resume processing.

## Path Traversal

Read-only application assets are resolved through controlled paths to prevent requests from accessing files outside their intended directories.

## Secrets

Secrets and credentials should never be committed to the repository.

Use:

```text
.env
```

for local secrets and:

```text
.env.example
```

for documenting required configuration variables.

---

# Testing

The project includes automated tests covering the primary application, ML, API, parser, security, and adversarial workflows.

Test categories include:

### API Tests

* endpoint behavior
* validation
* security headers
* path traversal
* SPA routes

### SaaS Feature Tests

* authentication
* dashboard
* jobs
* candidate pipeline
* analytics

### ATS Tests

* skill normalization
* structured parsing
* ATS diagnostics

### Ranking Tests

* TF-IDF calculations
* cosine similarity
* deterministic ranking

### Parser Tests

* PDF extraction
* DOCX extraction
* TXT extraction

### Preprocessing Tests

* token cleaning
* technical term preservation
* preprocessing behavior

### Adversarial Tests

The project also includes adversarial test cases designed to identify unexpected ranking and processing behavior.

## Run Tests

```bash
pytest -v tests/
```

Expected baseline:

```text
54 automated test suites
```

---

# Performance

For standard demonstration workloads, the screening pipeline is lightweight.

The current implementation has been observed to process approximately:

```text
12–50 candidate resumes
```

with execution times in the approximate range of:

```text
12–25 ms
```

for the core processing workflow under the tested local environment.

Typical memory consumption remains relatively low for demonstration-scale workloads.

Actual production performance will depend on:

* resume size
* number of candidates
* server resources
* document complexity
* deployment environment
* concurrent requests

Benchmark numbers should therefore be interpreted as local application measurements rather than universal production guarantees.

---

# Running Locally

## Prerequisites

Install:

* Python 3.9+
* pip
* Git

## 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ai-resume-screening-platform
```

## 2. Create a Virtual Environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a local `.env` file based on:

```text
.env.example
```

Never commit `.env`.

## 5. Start the Application

```bash
uvicorn backend.main:app --reload
```

The application should then be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# Environment Variables

The application supports the following configuration:

```env
ENVIRONMENT=production

HOST=0.0.0.0

PORT=8000

ALLOWED_ORIGINS=*

MAX_FILE_SIZE_MB=10

MAX_RESUMES_BATCH=50

LOG_LEVEL=INFO
```

## Configuration Reference

| Variable            | Purpose                                | Example               |
| ------------------- | -------------------------------------- | --------------------- |
| `ENVIRONMENT`       | Runtime environment                    | `production`          |
| `HOST`              | Server bind address                    | `0.0.0.0`             |
| `PORT`              | Server port                            | `8000`                |
| `ALLOWED_ORIGINS`   | Allowed frontend origins               | `https://example.com` |
| `MAX_FILE_SIZE_MB`  | Maximum resume size                    | `10`                  |
| `MAX_RESUMES_BATCH` | Maximum candidates per screening batch | `50`                  |
| `LOG_LEVEL`         | Application logging level              | `INFO`                |

For production deployment, replace permissive development settings with the minimum required access.

---

# Deployment

The application includes deployment configuration for container-based hosting as well as Vercel experimentation.

## Container Deployment

The repository includes:

```text
Dockerfile
Procfile
```

The application can be run as a persistent FastAPI/Uvicorn service.

Example:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Container-based deployment is advantageous for the current architecture because workspace mutations are held in Python process memory.

Suitable environments may include:

* Render
* Fly.io
* Railway
* Docker-based infrastructure
* other persistent container platforms

---

# Vercel Deployment

The repository also includes:

```text
vercel.json
```

for Vercel-compatible deployment.

The current architecture can be adapted to Vercel's serverless Python execution model.

However, there is an important architectural limitation.

The application currently maintains mutable workspace state in process memory.

For example:

* newly created jobs
* candidate stage changes
* workspace activity

may be reset when a serverless function instance is replaced or restarted.

Therefore:

> Vercel deployment is appropriate for a demonstration deployment, but persistent production SaaS usage should use an external database or persistent backend architecture.

For production-scale deployment, a recommended architecture is:

```text
                 ┌─────────────────┐
                 │    Frontend     │
                 │     Vercel      │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     FastAPI     │
                 │ Persistent API  │
                 └────────┬────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          Database    File Storage   ML/NLP
```

This would allow application state and uploaded candidate data to persist independently of backend process lifetime.

---

# Responsible AI

RankCraft AI is designed as a decision-support system.

The system should not be interpreted as an autonomous hiring decision-maker.

## Design Principles

### Explainability

Screening results should expose the evidence contributing to a candidate's score.

### Human Oversight

Recruiters remain responsible for final decisions.

### Data Minimization

Candidate information should only be processed when relevant to the screening workflow.

### Sensitive Attributes

Irrelevant sensitive characteristics should not be intentionally used for candidate ranking.

Examples include:

* gender
* age
* religion
* marital status
* photograph
* nationality
* other unrelated personal characteristics

### Limitations of Keyword-Based Screening

TF-IDF is fundamentally a statistical text representation method.

It can therefore be affected by:

* terminology differences
* synonyms
* keyword frequency
* resume formatting
* missing information
* unusual phrasing

A high screening score should therefore not be interpreted as proof that a candidate is objectively better qualified.

---

# Limitations

The current version is a research/prototype-oriented application rather than a fully productionized enterprise ATS.

Important limitations include:

## In-Memory State

Application state is currently stored in Python process memory.

Restarting the backend can reset mutable state.

## No External Database

The current version does not use PostgreSQL, MongoDB, or another persistent database.

## TF-IDF Limitations

TF-IDF measures lexical relevance rather than deep semantic equivalence.

Two resumes may describe similar experience using substantially different terminology and receive different similarity scores.

## Demonstration Dataset

The bundled dataset is intended for demonstration and evaluation.

It should not be interpreted as representative of the entire hiring population.

## Production File Storage

Custom uploads are processed in memory rather than using dedicated production object storage.

A production deployment would benefit from controlled object storage with appropriate security and retention policies.

## Authentication

The current authentication architecture is lightweight and intended for the prototype environment.

A production recruiting platform would require stronger identity, authorization, session management, audit logging, and organizational access controls.

---

# Research Context

The project explores the use of natural-language processing and machine-learning techniques for automated resume screening.

The central research question is:

> Can deterministic NLP and multi-factor candidate matching provide a useful, transparent mechanism for prioritizing resumes against a target job description?

The implementation focuses on:

* document processing
* NLP preprocessing
* TF-IDF representation
* cosine similarity
* skill normalization
* structured candidate attributes
* explainable screening
* adversarial evaluation

The architecture intentionally favors interpretability and reproducibility over opaque end-to-end prediction.

---

# Future Improvements

Potential future development directions include:

### Persistent Data Layer

Introduce PostgreSQL or another production database for:

* users
* organizations
* jobs
* candidates
* pipeline stages
* activity logs

### Object Storage

Move resume storage to secure object storage such as:

* Amazon S3
* Cloudflare R2
* Google Cloud Storage

with appropriate access controls.

### Semantic Search

Evaluate transformer-based embeddings alongside TF-IDF to improve semantic matching.

### Hybrid Ranking

Combine:

```text
TF-IDF
+
Semantic Similarity
+
Skill Matching
+
Experience Matching
+
Education Matching
```

while maintaining explainability.

### Advanced Evaluation

Evaluate the system using:

* precision
* recall
* F1
* ranking metrics
* false-positive analysis
* false-negative analysis
* robustness tests
* fairness-oriented evaluations

### Enterprise Access Control

Introduce role-based permissions for:

* recruiters
* hiring managers
* administrators
* candidates

### Production Observability

Add:

* structured logging
* metrics
* tracing
* error monitoring
* performance monitoring

---

# Project Status

## Current Capabilities

* [x] Resume ingestion
* [x] PDF parsing
* [x] DOCX parsing
* [x] TXT parsing
* [x] NLP preprocessing
* [x] PII-oriented preprocessing
* [x] Skill normalization
* [x] TF-IDF vectorization
* [x] Cosine similarity
* [x] Structured candidate matching
* [x] ATS parseability diagnostics
* [x] Candidate ranking
* [x] Candidate pipeline
* [x] Job management
* [x] Screening workspace
* [x] Candidate profiles
* [x] Analytics
* [x] Automated testing
* [x] Security-oriented validation
* [x] Container deployment configuration
* [x] Vercel deployment configuration

---

# Contributing

Contributions are welcome.

Before submitting a pull request:

1. Explain the problem being solved.
2. Describe the implementation.
3. Add or update tests.
4. Verify that existing functionality remains intact.
5. Document meaningful architectural changes.
6. Avoid committing secrets or sensitive candidate data.

---

# Security

If you discover a security vulnerability, do not publicly disclose sensitive exploit details before the issue can be addressed.

Please report security issues privately to the repository maintainer.

---

# License

This project is provided for research, educational, and demonstration purposes.

If this repository is intended to use an open-source license, add the appropriate license file here.

---

## Disclaimer

RankCraft AI is an AI-assisted candidate screening and decision-support system.

It is not a substitute for qualified human judgment, professional recruitment practices, or applicable employment and anti-discrimination requirements.

Screening scores are model-derived signals and should not be treated as definitive measures of candidate suitability.

---

# Built With

```text
Python
FastAPI
Uvicorn
scikit-learn
NumPy
pypdf
python-docx
HTML5
CSS3
JavaScript
pytest
```

---

## Architecture at a Glance

```text
┌─────────────────────────────────────────────┐
│               RankCraft AI                  │
│                                             │
│        Intelligent Recruiting Workspace     │
└──────────────────────┬──────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
  Recruiter UI                  FastAPI API
        │                             │
        │                    ┌────────┴────────┐
        │                    │                 │
        ▼                    ▼                 ▼
    Jobs &             Resume Parser      ML Ranking
   Candidates               │                 │
                            ▼                 ▼
                       Preprocessing     TF-IDF
                            │           + Cosine
                            ▼                 │
                       Skill Taxonomy         │
                            │                 │
                            └────────┬────────┘
                                     ▼
                              Screening Score
                                     │
                                     ▼
                              Candidate Ranking
                                     │
                                     ▼
                              Human Decision
```

---

## Final Principle

**RankCraft AI does not decide who should be hired.**

It helps recruiters answer a narrower question:

> **"Which candidates should I review first, and what evidence explains their ranking?"**
