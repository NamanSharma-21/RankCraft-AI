# Demonstration Script & Presentation Guide
## RankCraft AI: Multi-Factor ATS Resume Screening & Candidate Ranking System

**Capstone Option:** Option 2 — AI Resume Screening & Candidate Ranking System  
**Presentation Target Duration:** 5–7 Minutes (Max 10 Minutes)  
**Speaker Language:** English (Clear, professional, academic delivery)  

---

## 🕒 5–7 Minute Presentation Sequence

```
+------------------+-----------------------------------------------------------+
| Timestamp        | Presentation Stage                                        |
+------------------+-----------------------------------------------------------+
| 0:00 - 0:45      | Introduction (Student, Project Title, Program, Capstone)  |
| 0:45 - 1:30      | Problem Statement & Engineering Motivation                |
| 1:30 - 2:15      | System Architecture & Technology Stack                    |
| 2:15 - 4:30      | Live Application Walkthrough & ATS Prototype Demo         |
| 4:30 - 5:30      | Machine Learning Methodology & Multi-Factor Scoring       |
| 5:30 - 6:30      | Quantitative Benchmark & Adversarial Case Studies         |
| 6:30 - 7:00      | Limitations, Ethical Guardrails & Conclusion              |
+------------------+-----------------------------------------------------------+
```

---

### [0:00 – 0:45] Stage 1: Introduction
> **Visual On Screen:** Browser opened to `http://127.0.0.1:8000` showing the RankCraft AI ATS dashboard header.

**Spoken Script:**
> *"Hello everyone and esteemed evaluators. My name is [Your Name], and today I am presenting my final capstone project for the LaunchED Artificial Intelligence Major Capstone Program: **RankCraft AI — Multi-Factor ATS Resume Screening & Candidate Ranking System**.*
>
> *Recruiting teams receive hundreds of unstructured resumes for every open position. The goal of this project is to build an explainable, deterministic, and high-performance NLP prototype that ingests multi-format candidate resumes, evaluates them using TF-IDF and Cosine Similarity, extracts structured profiles, and ranks candidates using transparent multi-factor scoring with ATS parseability diagnostics."*

---

### [0:45 – 1:30] Stage 2: Problem Statement & Engineering Motivation
> **Visual On Screen:** Job description textarea and resume upload dropzone.

**Spoken Script:**
> *"Recruiters face four key bottlenecks during first-pass screening:*
> 1. *First, **Document Diversity:** Resumes arrive in disparate formats like PDF, Word DOCX, and raw text.*
> 2. *Second, **Preprocessing Pitfalls:** Standard NLP tools strip punctuation, destroying compound technical terms like `C++`, `.NET`, `CI/CD`, and `FastAPI`.*
> 3. *Third, **Keyword Stuffing vs Abbreviations:** Pure keyword matchers can be gamed by repetitive buzzwords while penalizing legitimate candidates using abbreviations like `ML`, `NLP`, or `K8s`.*
> 4. *Fourth, **Black-Box Opacity:** While LLMs are popular, in initial candidate triage they introduce latency, steep API operating costs, hallucinations, and non-deterministic scoring.*
>
> *RankCraft AI solves this through a deterministic statistical NLP engine operating in under 15 milliseconds, coupled with structured skill normalization and multi-factor alignment."*

---

### [1:30 – 2:15] Stage 3: System Architecture & Tech Stack
> **Visual On Screen:** Show `results/architecture_diagram.png` or the system architecture diagram.

**Spoken Script:**
> *"The system is built on a clean, decoupled five-layer architecture:*
> - *The **Presentation Layer** is a modern, responsive web client crafted in semantic HTML5, CSS3, and vanilla JavaScript.*
> - *The **API Layer** is powered by FastAPI, exposing high-performance RESTful endpoints with automatic OpenAPI Swagger documentation.*
> - *The **Ingestion & Structured Parsing Layer** uses `pypdf` and `python-docx` to extract text and parse candidate contact information, work experience timelines, and degrees.*
> - *The **Skill Taxonomy Layer** uses a configurable JSON dictionary to normalize aliases and abbreviations and segment skills into Required vs Preferred.*
> - *And the **ML Ranking Layer** transforms documents into a common sublinear TF-IDF vector space to compute directional Cosine Similarities and composite Screening Scores."*

---

### [2:15 – 4:30] Stage 4: Live Application Walkthrough
> **Visual On Screen:** Switch to the live web interface at `http://127.0.0.1:8000`.

**Step-by-Step Live Actions to Perform:**

1. **Step 1: 1-Click Instant Demo**
   - Click the top purple banner button: **"🚀 1-Click Instant Demo"**.
   - *Spoken:* *"Let's trigger our 1-Click Instant Demo. The backend immediately parses 12 pre-loaded candidate resumes across PDF, DOCX, and TXT formats against the Senior AI/ML Engineer job description."*

2. **Step 2: Inspecting Ranked Candidate Cards & Multi-Metric Breakdown**
   - Point to Rank #1: **Dr. Alex Rivera** (Screening Score: `78.3%`, TF-IDF: `30.1%`, Skill Coverage: `87.5%`).
   - *Spoken:* *"Notice that Dr. Alex Rivera is ranked #1. Each card presents a multi-metric breakdown: TF-IDF Cosine Match, Skill Coverage %, Title Match %, Experience Tenure %, Education Level %, and ATS Health Score."*
   - Point to the green **Matched Skills** pills, red **Missing Required** pills, and the **'Why this candidate ranked here'** explainability narrative.

3. **Step 3: Demonstrating Candidate Detail & 8-Point ATS Parseability Modal**
   - Click **"📋 Full Profile & ATS Audit"** on Rank #1.
   - *Spoken:* *"Clicking 'Full Profile & ATS Audit' opens our diagnostic modal. It details candidate email, phone, professional summary, work experience timeline, degrees, and an 8-point ATS parseability checklist with green checkmarks indicating clean text, timeline extraction, and contact detection."*
   - Close modal.

4. **Step 4: Demonstrating Candidate Comparison Matrix**
   - Click **"📊 Compare Candidates"** at the top right of the results panel.
   - *Spoken:* *"Recruiters can click 'Compare Candidates' to open a side-by-side comparison matrix, allowing instant cross-candidate evaluation across all 6 scoring dimensions and missing skills."*
   - Close modal.

5. **Step 5: Demonstrating CSV Export**
   - Click **"📥 Export CSV"**.
   - *Spoken:* *"Recruiters can export the complete structured rankings, sub-scores, and explainability narratives to CSV with a single click for downstream ATS workflows."*

---

### [4:30 – 5:30] Stage 5: Machine Learning Methodology & Multi-Factor Scoring
> **Visual On Screen:** Open `notebooks/Resume_Screening_Analysis.ipynb` or show report formulas.

**Spoken Script:**
> *"Let's review the mathematical foundation:*
> - *We vectorize documents using **Sublinear Term Frequency** scaling, $1 + \log(\text{TF})$, ensuring long resumes cannot artificially dominate scores through repetitive keyword stuffing.*
> - *We apply **Smoothed Inverse Document Frequency** and $L_2$-normalize all vectors, so Cosine Similarity computes as the dot product: $\sum u_i v_i$.*
> - *To provide holistic screening, we calculate a transparent, project-defined **Composite Screening Score**:*
>   $$\text{Screening Score} = 0.40 \times \text{TF-IDF} + 0.25 \times \text{Skills} + 0.15 \times \text{Title} + 0.10 \times \text{Experience} + 0.10 \times \text{Education}$$
> - *Ranking is strictly deterministic: sorting descending by Screening Score, with secondary TF-IDF and candidate ID tie-breaking."*

---

### [5:30 – 6:30] Stage 6: Quantitative Benchmark & Adversarial Case Studies
> **Visual On Screen:** Show `results/score_distribution.png` and `results/adversarial_comparison.png`.

**Spoken Script:**
> *"We evaluated the system across two rigorous benchmarks:*
> - *On our standard 3-role benchmark (36 ground-truth annotations), the system achieved **100% Precision@1**, **100% Precision@3**, **80% Precision@5**, and an overall **MAP of 0.9611** and **NDCG@5 of 0.9594**.*
> - *Furthermore, in our 8-case adversarial benchmark, we specifically tested edge cases like **Keyword Stuffing** (Case D, an Enterprise Sales Director copying ML buzzwords). While pure TF-IDF gave Case D high lexical scores, our multi-factor engine penalized the candidate's sales title and marketing degree to Rank #5, successfully preventing false-positive shortlisting.*
> - *Additionally, our configurable skill taxonomy successfully recovered scores for candidates using abbreviations like `K8s`, `ML`, and `DL` (Case C) and synonyms (Case B)."*

---

### [6:30 – 7:00] Stage 7: Limitations, Ethical Guardrails & Conclusion
> **Visual On Screen:** Summary view of the RankCraft AI dashboard.

**Spoken Script:**
> *"In terms of ethical safeguards and limitations:*
> - *Our preprocessing pipeline scrubs personal contact details (email, phone, URLs), and the ranking engine strictly ignores protected demographic attributes like gender, age, race, and photo.*
> - *We recognize that TF-IDF operates on statistical lexical matching and cannot resolve abstract descriptive phrasing without keyword expansion—an ideal area for future hybrid Sentence-BERT reranking.*
> - *Most importantly, this system is designed strictly for **first-pass decision support** with human recruiters always in the loop.*
>
> *Thank you for your time, and I welcome any questions."*

---

## 📱 LaunchED Submission Deliverables Templates

### Template A: LinkedIn Post Draft
*(Copy, customize bracketed info, and post on LinkedIn with your project screenshot/video)*

```markdown
🚀 Excited to share my Final Capstone Project for the LaunchED Artificial Intelligence Major Program: "RankCraft AI — Multi-Factor ATS Resume Screening & Candidate Ranking System"!

Triage of incoming resumes is one of the biggest bottlenecks in recruitment. In this project, I engineered an explainable, deterministic NLP candidate screening prototype from the ground up:

🔹 Multi-Format Ingestion: Robust text extraction for PDF, DOCX, and TXT resumes.
🔹 Domain-Aware NLP: Custom preprocessing preserving compound technical tokens (C++, .NET, CI/CD, Scikit-Learn, FastAPI) while stripping PII for demographic neutrality.
🔹 Configurable Skill Taxonomy: Deterministic normalization resolving abbreviations (ML, NLP, K8s, Postgres) and distinguishing Required vs Preferred qualifications.
🔹 TF-IDF & Multi-Factor Screening Score: Sublinear feature vectorization combined with transparent title, experience, and education matching.
🔹 8-Point ATS Parseability Diagnostic: Automated audit of extractability, contact info, and timeline validity.
🔹 Full-Stack App: Built with a FastAPI backend, interactive web dashboard, candidate comparison matrix, and 1-click CSV export.
🔹 Rigorous Evaluation: Benchmarked across 36 ground-truth annotations and 8 adversarial stress cases achieving 100% Precision@1, 100% Precision@3, and 0.9594 NDCG@5.

A huge thank you to the mentors and community at LaunchED Global for an incredible learning journey!

#ArtificialIntelligence #MachineLearning #NLP #Python #FastAPI #DataScience #LaunchED #CapstoneProject #AI #ATS
```

---

### Template B: Google Review Draft for LaunchED Global
*(Copy, customize, and submit on LaunchED Global's Google Review page)*

```markdown
The LaunchED Artificial Intelligence Capstone Program has been an exceptional and transformative hands-on learning experience. The curriculum provided the perfect balance between foundational machine learning principles, rigorous mathematical formulation, and end-to-end full-stack software engineering. Building the Multi-Factor ATS Resume Screening & Candidate Ranking System as my major capstone gave me deep practical experience in NLP pipeline design, FastAPI backend development, and information retrieval evaluation. Highly recommended for any aspiring AI/ML engineer!
```
