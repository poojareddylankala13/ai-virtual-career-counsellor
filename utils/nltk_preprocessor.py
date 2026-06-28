import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Auto-download required NLTK datasets
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet", quiet=True)

try:
    nltk.data.find("corpora/omw-1.4")
except LookupError:
    nltk.download("omw-1.4", quiet=True)


class NLTKPreprocessor:
    """
    A utility class to perform NLTK preprocessing on user input text.
    Handles tokenization, stop-word filtering, punctuation removal,
    lemmatization, and domain/skill keyword matching.
    """

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))

    def preprocess(self, text: str) -> list:
        """
        Runs the full text preprocessing pipeline:
        1. Lowercasing
        2. Tokenization
        3. Punctuation removal
        4. Stop-word removal
        5. Lemmatization
        """
        if not text or not isinstance(text, str):
            return []

        # 1. Lowercasing & Punctuation removal (regex-based)
        text_clean = re.sub(r"[^\w\s]", " ", text.lower())

        # 2. Tokenization
        tokens = word_tokenize(text_clean)

        # 3. Stop-word removal & 4. Lemmatization
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and token.strip():
                # Lemmatize both noun and verb forms
                lemma = self.lemmatizer.lemmatize(token, pos="v")
                lemma = self.lemmatizer.lemmatize(lemma, pos="n")
                processed_tokens.append(lemma)

        return processed_tokens

    def extract_keywords(self, text: str, reference_keywords: list) -> list:
        """
        Extracts keywords from input text by checking overlap with a reference list of words.
        Uses lemmatized comparisons for high accuracy.
        """
        if not text or not reference_keywords:
            return []

        processed_input = self.preprocess(text)
        
        # Lemmatize and clean the reference keywords as well for accurate comparison
        ref_map = {}
        for rk in reference_keywords:
            # We map the lemmatized version to the original string representation
            cleaned_ref = re.sub(r"[^\w\s]", " ", rk.lower()).strip()
            ref_tokens = [self.lemmatizer.lemmatize(t, pos="v") for t in word_tokenize(cleaned_ref)]
            ref_tokens = [self.lemmatizer.lemmatize(t, pos="n") for t in ref_tokens]
            # Convert tokens list to a space-separated signature
            signature = " ".join(ref_tokens)
            ref_map[signature] = rk

        found_keywords = set()
        input_signature = " ".join(processed_input)

        # Match direct keywords and multi-word keywords
        for signature, original_val in ref_map.items():
            if signature in input_signature or any(token in processed_input for token in signature.split()):
                found_keywords.add(original_val)

        return list(found_keywords)
