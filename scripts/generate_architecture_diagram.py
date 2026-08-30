"""
Generate Architecture and Pipeline Diagram for Project Documentation and Report
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["MPLCONFIGDIR"] = os.path.join(BASE_DIR, ".matplotlib_cache")

import matplotlib.pyplot as plt
import matplotlib.patches as patches

RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def draw_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")

    # Colors
    c_input = "#eff6ff"
    c_input_b = "#3b82f6"
    c_proc = "#f0fdf4"
    c_proc_b = "#10b981"
    c_ml = "#fef3c7"
    c_ml_b = "#f59e0b"
    c_out = "#f5f3ff"
    c_out_b = "#8b5cf6"

    # Box 1: Input Layer
    rect1 = patches.FancyBboxPatch((4, 18), 18, 30, boxstyle="round,pad=1", facecolor=c_input, edgecolor=c_input_b, linewidth=2)
    ax.add_patch(rect1)
    ax.text(13, 44, "1. Input Layer", fontsize=11, fontweight="bold", ha="center", color="#1e3a8a")
    ax.text(13, 38, "Job Description\n(Text / TXT)\n\nCandidate Resumes\n(PDF, DOCX, TXT)", fontsize=9, ha="center", color="#1e293b")

    # Arrow 1 -> 2
    ax.annotate('', xy=(26, 33), xytext=(22, 33),
                arrowprops=dict(facecolor='#64748b', edgecolor='#64748b', width=2, headwidth=8))

    # Box 2: Processing Layer
    rect2 = patches.FancyBboxPatch((28, 14), 20, 38, boxstyle="round,pad=1", facecolor=c_proc, edgecolor=c_proc_b, linewidth=2)
    ax.add_patch(rect2)
    ax.text(38, 48, "2. Processing Layer", fontsize=11, fontweight="bold", ha="center", color="#065f46")
    ax.text(38, 32, "Multi-format Extraction\n(pypdf, python-docx)\n\nPII Anonymization\n(strip email/phone/url)\n\nTech Term Preservation\n(C++, .NET, CI/CD, etc.)\n\nStopword Filtering", fontsize=8.5, ha="center", color="#1e293b")

    # Arrow 2 -> 3
    ax.annotate('', xy=(52, 33), xytext=(48, 33),
                arrowprops=dict(facecolor='#64748b', edgecolor='#64748b', width=2, headwidth=8))

    # Box 3: NLP & ML Layer
    rect3 = patches.FancyBboxPatch((54, 14), 20, 38, boxstyle="round,pad=1", facecolor=c_ml, edgecolor=c_ml_b, linewidth=2)
    ax.add_patch(rect3)
    ax.text(64, 48, "3. ML & Ranking Layer", fontsize=11, fontweight="bold", ha="center", color="#92400e")
    ax.text(64, 32, "Unified Corpus Building\n[Clean JD + Resumes]\n\nTF-IDF Vectorizer\n(Sublinear TF, 1-2 N-grams)\n\nCosine Similarity\n(Angle in Feature Space)\n\nDeterministic Sort\n(Score desc, ID tie-break)", fontsize=8.5, ha="center", color="#1e293b")

    # Arrow 3 -> 4
    ax.annotate('', xy=(78, 33), xytext=(74, 33),
                arrowprops=dict(facecolor='#64748b', edgecolor='#64748b', width=2, headwidth=8))

    # Box 4: Output & Presentation Layer
    rect4 = patches.FancyBboxPatch((80, 18), 16, 30, boxstyle="round,pad=1", facecolor=c_out, edgecolor=c_out_b, linewidth=2)
    ax.add_patch(rect4)
    ax.text(88, 44, "4. Output Layer", fontsize=11, fontweight="bold", ha="center", color="#5b21b6")
    ax.text(88, 34, "FastAPI REST API\n(JSON Response)\n\nWeb Dashboard\n(Ranks, Scores)\n\nExplainability\n(Matched/Missing Terms)", fontsize=8.5, ha="center", color="#1e293b")

    # Title
    ax.text(50, 56, "AI Resume Screening & Candidate Ranking System Architecture", fontsize=14, fontweight="bold", ha="center", color="#0f172a")

    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, "architecture_diagram.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated architecture diagram: {out_path}")


if __name__ == "__main__":
    draw_architecture_diagram()
