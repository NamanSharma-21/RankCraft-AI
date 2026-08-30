"""
Unit tests for text preprocessing & normalization
"""

import pytest
from backend.preprocessing import (
    preprocess_text,
    clean_text_pii_and_noise,
    preserve_tech_terms,
    tokenize
)


def test_pii_stripping():
    sample = "Contact John at john.doe@example.com or call (555) 123-4567. Visit https://johndoe.dev"
    cleaned = clean_text_pii_and_noise(sample)
    assert "john.doe@example.com" not in cleaned
    assert "555" not in cleaned
    assert "https://" not in cleaned


def test_tech_term_preservation():
    sample = "Proficient in C++, C#, .NET, Node.js, and CI/CD pipelines with Scikit-Learn and TF-IDF."
    normalized = preserve_tech_terms(sample)
    assert "cpp" in normalized
    assert "csharp" in normalized
    assert "dotnet" in normalized
    assert "nodejs" in normalized
    assert "cicd" in normalized
    assert "scikitlearn" in normalized
    assert "tfidf" in normalized


def test_preprocess_text_empty_and_null():
    assert preprocess_text("") == ""
    assert preprocess_text(None) == ""
    assert preprocess_text("   ") == ""


def test_preprocess_text_stopwords_removal():
    sample = "This is a detailed summary of the key requirements and work experience."
    processed = preprocess_text(sample)
    # Stopwords like 'this', 'is', 'a', 'of', 'the', 'and' should be removed
    tokens = processed.split()
    assert "this" not in tokens
    assert "is" not in tokens
    assert "detailed" in tokens


def test_tokenize_output():
    sample = "Machine Learning Python FastAPI Docker"
    tokens = tokenize(sample)
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    assert "python" in tokens
    assert "fastapi" in tokens
