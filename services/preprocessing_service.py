"""
Preprocessing Service
Handles NLTK initialization, text normalization, tokenization, sentence segmentation, and stats.
"""

import re
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Flag to track if NLTK data is downloaded
_NLTK_INITIALIZED = False

def _setup_nltk():
    """Download required NLTK datasets once per process."""
    global _NLTK_INITIALIZED
    if _NLTK_INITIALIZED:
        return
    
    import nltk
    
    # Required packages
    packages = ["punkt", "punkt_tab", "stopwords"]
    
    for package in packages:
        try:
            nltk.data.find(f"tokenizers/{package}")
        except LookupError:
            try:
                nltk.data.find(f"corpora/{package}")
            except LookupError:
                logger.info(f"Downloading NLTK package: {package}")
                nltk.download(package, quiet=True)
                
    _NLTK_INITIALIZED = True


class PreprocessingService:
    """Service for basic NLP preprocessing tasks."""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text: lowercase, whitespace normalization, punctuation spacing.
        """
        if not text:
            return ""
            
        # 1. Lowercase
        normalized = text.lower()
        
        # 2. Normalize whitespace (replace multiple spaces/newlines with single space)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 3. Normalize punctuation spacing (ensure space after punctuation if missing, unless it's a number)
        # We avoid complex regex here that might break URLs or decimals, keeping it simple for text.
        normalized = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', normalized)
        
        return normalized.strip()

    @staticmethod
    def segment_sentences(text: str) -> List[str]:
        """Segment raw text into sentences using NLTK."""
        if not text:
            return []
        
        _setup_nltk()
        from nltk.tokenize import sent_tokenize
        
        return sent_tokenize(text)

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words using NLTK."""
        if not text:
            return []
            
        _setup_nltk()
        from nltk.tokenize import word_tokenize
        
        return word_tokenize(text)

    @classmethod
    def run_preprocessing(cls, raw_text: str) -> Dict[str, Any]:
        """
        Run the complete preprocessing pipeline on raw text.
        Returns a dictionary with normalized text, sentences, tokens, and statistics.
        """
        # 1. Normalize
        normalized_text = cls.normalize_text(raw_text)
        
        # 2. Sentence Segmentation
        sentences = cls.segment_sentences(raw_text) # Using raw_text for better sentence boundary detection
        sentence_count = len(sentences)
        
        # 3. Tokenization
        tokens = cls.tokenize(normalized_text)
        token_count = len(tokens)
        
        # 4. Statistics
        unique_tokens = set(tokens)
        unique_token_count = len(unique_tokens)
        vocabulary_size = unique_token_count
        
        avg_sentence_length = 0.0
        if sentence_count > 0:
            avg_sentence_length = token_count / sentence_count
            
        return {
            "normalized_text": normalized_text,
            "sentences": sentences,
            "tokens": tokens,
            "token_count": token_count,
            "sentence_count": sentence_count,
            "unique_token_count": unique_token_count,
            "vocabulary_size": vocabulary_size,
            "average_sentence_length": round(avg_sentence_length, 2)
        }
