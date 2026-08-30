"""
Unit tests for resume document parsers (PDF, DOCX, TXT)
"""

import os
import io
import pytest
from backend.resume_parser import (
    parse_resume,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_candidate_name,
    UnsupportedFormatError,
    FileExtractionError
)

DATA_RESUMES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "resumes")


def test_parse_pdf_resume():
    pdf_path = os.path.join(DATA_RESUMES, "candidate_01_senior_ml_engineer.pdf")
    if os.path.exists(pdf_path):
        res = parse_resume(pdf_path, "candidate_01_senior_ml_engineer.pdf")
        assert res["file_type"] == "PDF"
        assert "Alex Rivera" in res["candidate_name"] or "Dr. Alex Rivera" in res["candidate_name"]
        assert len(res["raw_text"]) > 100
        assert res["word_count"] > 20


def test_parse_docx_resume():
    docx_path = os.path.join(DATA_RESUMES, "candidate_02_nlp_data_scientist.docx")
    if os.path.exists(docx_path):
        res = parse_resume(docx_path, "candidate_02_nlp_data_scientist.docx")
        assert res["file_type"] == "DOCX"
        assert "Sarah Chen" in res["candidate_name"]
        assert "Machine Learning" in res["raw_text"]


def test_parse_txt_resume():
    txt_path = os.path.join(DATA_RESUMES, "candidate_04_backend_python_engineer.txt")
    if os.path.exists(txt_path):
        res = parse_resume(txt_path, "candidate_04_backend_python_engineer.txt")
        assert res["file_type"] == "TXT"
        assert "Elena Rostova" in res["candidate_name"]
        assert "FastAPI" in res["raw_text"]


def test_unsupported_file_format():
    with pytest.raises(UnsupportedFormatError):
        parse_resume(b"fake data", "resume.png")


def test_empty_file_extraction_error():
    with pytest.raises(FileExtractionError):
        parse_resume(b"", "empty_resume.txt")


def test_extract_candidate_name_fallback():
    name = extract_candidate_name("", "candidate_05_senior_data_analyst.pdf")
    assert "Senior Data Analyst" in name or "David Kim" in name
