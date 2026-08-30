"""
NLP Preprocessing Module
Performs domain-aware text cleaning, normalization, and token preservation
for resumes and job descriptions.
"""

import re
from typing import List, Set

# Domain-specific tech terms mapped to unified unigrams to prevent
# punctuation-stripping from destroying key skills (e.g. C++ -> cpp, .NET -> dotnet).
TECH_TERM_MAPPINGS = [
    (r"(?i)\bc\+\+(?!\w)", "cpp"),
    (r"(?i)\bc#(?!\w)", "csharp"),
    (r"(?i)\.net(?!\w)", "dotnet"),
    (r"(?i)\bnode\.js(?!\w)", "nodejs"),
    (r"(?i)\bnext\.js(?!\w)", "nextjs"),
    (r"(?i)\bvue\.js(?!\w)", "vuejs"),
    (r"(?i)\bci/cd(?!\w)", "cicd"),
    (r"(?i)\bci-cd(?!\w)", "cicd"),
    (r"(?i)\bscikit-learn(?!\w)", "scikitlearn"),
    (r"(?i)\bscikit_learn(?!\w)", "scikitlearn"),
    (r"(?i)\btf-idf(?!\w)", "tfidf"),
    (r"(?i)\btf_idf(?!\w)", "tfidf"),
    (r"(?i)\bpower\s+bi(?!\w)", "powerbi"),
    (r"(?i)\brestful\s+apis?(?!\w)", "restapi"),
    (r"(?i)\brest\s+apis?(?!\w)", "restapi"),
    (r"(?i)\bpostgres(?:ql)?(?!\w)", "postgresql"),
    (r"(?i)\bms\s+excel(?!\w)", "excel"),
    (r"(?i)\bms\s+sql(?!\w)", "mssql"),
    (r"(?i)\bpl/pgsql(?!\w)", "plpgsql"),
    (r"(?i)\ba/b\s+testing(?!\w)", "abtesting"),
]

# Standard English stopwords
DEFAULT_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing",
    "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom",
    "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves", "also", "including", "per", "via", "using", "work", "experience",
    "years", "responsibilities", "requirements", "summary", "skills"
}


def clean_text_pii_and_noise(text: str) -> str:
    """
    Strips email addresses, URLs, phone numbers, and non-printable noise
    to prevent leaking PII and reduce vocabulary noise.
    """
    if not text:
        return ""

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Remove email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)
    # Remove phone number patterns
    text = re.sub(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", " ", text)
    # Normalize bullet points and weird dashes
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u25CB\u25CF\u25A0\u2013\u2014]", " ", text)
    
    return text


def preserve_tech_terms(text: str) -> str:
    """
    Replaces compound and punctuated technical terms with normalized tokens.
    """
    output = text
    for pattern, replacement in TECH_TERM_MAPPINGS:
        output = re.sub(pattern, replacement, output)
    return output.lower()


def preprocess_text(text: str, remove_stopwords: bool = True) -> str:
    """
    Main preprocessing pipeline:
    1. Strip PII (email, phone, URL) & noise
    2. Map domain-specific tech terms (C++ -> cpp, etc.)
    3. Remove punctuation and non-alphanumeric chars
    4. Normalize whitespace
    5. Optionally filter out stopwords
    """
    if not text or not isinstance(text, str):
        return ""

    # Step 1: Clean noise and PII
    cleaned = clean_text_pii_and_noise(text)

    # Step 2: Preserve tech terms & lower
    normalized = preserve_tech_terms(cleaned)

    # Step 3: Remove punctuation (replace with spaces)
    # Keep alphanumeric tokens
    no_punct = re.sub(r"[^\w\s]", " ", normalized)

    # Step 4: Tokenize & remove numbers-only words or single characters
    tokens = no_punct.split()
    filtered_tokens = []
    
    for t in tokens:
        t = t.strip()
        # Drop standalone pure digits and 1-letter tokens
        if len(t) <= 1 or t.isdigit():
            continue
        if remove_stopwords and t in DEFAULT_STOPWORDS:
            continue
        filtered_tokens.append(t)

    return " ".join(filtered_tokens)


def tokenize(text: str) -> List[str]:
    """Tokenizes preprocessed text into word list."""
    cleaned = preprocess_text(text)
    return cleaned.split()
