import sys
import os
import pytest

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.nltk_preprocessor import NLTKPreprocessor


def test_preprocessing_pipeline():
    preprocessor = NLTKPreprocessor()
    
    test_text = "I am creating software programs with Python!"
    expected_tokens = ["create", "software", "program", "python"]
    
    tokens = preprocessor.preprocess(test_text)
    
    # Assert token list contains correct elements and is cleaned
    for item in expected_tokens:
        assert item in tokens
    assert "am" not in tokens  # Stop-word check
    assert "with" not in tokens  # Stop-word check
    assert "!" not in tokens  # Punctuation check


def test_keyword_extraction():
    preprocessor = NLTKPreprocessor()
    
    test_text = "I want a career in financial markets and auditing transactions."
    reference = ["Financial Analyst", "AI Engineer", "Auditing", "Marketing Manager"]
    
    # Extract keywords
    extracted = preprocessor.extract_keywords(test_text, reference)
    
    # "Financial Analyst" has "financial", which matches the test text.
    # "Auditing" is a direct match.
    assert "Financial Analyst" in extracted
    assert "Auditing" in extracted
    assert "AI Engineer" not in extracted
