"""
Morphology Service
Handles POS-aware lemmatization, Porter Stemming, and explainable morphology mapping.
"""

import logging
from typing import Dict, Any, List, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

# Flag to track if NLTK morphology data is downloaded
_NLTK_MORPHOLOGY_INITIALIZED = False

def _setup_nltk_morphology():
    """Download required NLTK datasets for morphology once per process."""
    global _NLTK_MORPHOLOGY_INITIALIZED
    if _NLTK_MORPHOLOGY_INITIALIZED:
        return
    
    import nltk
    
    # Required packages for POS tagging and Lemmatization
    packages = ["averaged_perceptron_tagger", "averaged_perceptron_tagger_eng", "wordnet", "omw-1.4"]
    
    for package in packages:
        try:
            # Check corpora or taggers
            if "tagger" in package:
                nltk.data.find(f"taggers/{package}")
            else:
                nltk.data.find(f"corpora/{package}")
        except LookupError:
            logger.info(f"Downloading NLTK package: {package}")
            try:
                nltk.download(package, quiet=True)
            except Exception as e:
                logger.warning(f"Failed to download NLTK package {package}: {e}")
                
    _NLTK_MORPHOLOGY_INITIALIZED = True

def _get_wordnet_pos(treebank_tag: str) -> str:
    """Map NLTK POS tag (treebank) to WordNet POS tag."""
    from nltk.corpus import wordnet
    
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        # Default to noun
        return wordnet.NOUN

def _generate_stem_explanation(token: str, stem: str) -> str:
    """Generate human-readable explanation for stemming."""
    if token == stem:
        return "No morphological change required."
    
    # Rough heuristics for explanation
    if token.endswith("ing") and stem == token[:-3]:
        return "Porter Stemmer removed present participle suffix '-ing'."
    elif token.endswith("ing") and not stem.endswith("ing"):
        return "Porter Stemmer handled '-ing' suffix."
    elif token.endswith("es") and stem == token[:-2]:
        return "Porter Stemmer removed plural/third-person suffix '-es'."
    elif token.endswith("s") and stem == token[:-1]:
        return "Porter Stemmer removed plural/third-person suffix '-s'."
    elif token.endswith("ed") and not stem.endswith("ed"):
        return "Porter Stemmer removed past tense suffix '-ed'."
    elif token.endswith("ly") and not stem.endswith("ly"):
        return "Porter Stemmer removed adverbial suffix '-ly'."
    else:
        return f"Porter stemming rules applied to reduce to root '{stem}'."

def _generate_lemma_explanation(token: str, lemma: str, pos_tag: str) -> str:
    """Generate human-readable explanation for lemmatization."""
    if token.lower() == lemma.lower():
        return "Token is already in its base dictionary form."
        
    from nltk.corpus import wordnet
    pos_name = "Word"
    if pos_tag == wordnet.VERB:
        pos_name = "Verb"
    elif pos_tag == wordnet.NOUN:
        pos_name = "Noun"
    elif pos_tag == wordnet.ADJ:
        pos_name = "Adjective"
    elif pos_tag == wordnet.ADV:
        pos_name = "Adverb"
        
    return f"{pos_name} normalized to its base dictionary form."


class MorphologyService:
    """Service for NLP morphological analysis (stemming and lemmatization)."""

    @classmethod
    def run_morphology(cls, tokens: List[str]) -> Dict[str, Any]:
        """
        Run the morphology pipeline on a list of tokens.
        Returns stemmed arrays, lemmatized arrays, mapping pairs, and vocabulary reduction stats.
        """
        if not tokens:
            return {
                "stemmed_tokens": [],
                "lemmatized_tokens": [],
                "morphology_pairs": [],
                "unique_stems": 0,
                "unique_lemmas": 0,
                "stem_count": 0,
                "lemma_count": 0,
                "original_vocabulary_size": 0,
                "stemmed_vocabulary_size": 0,
                "lemmatized_vocabulary_size": 0,
                "vocabulary_reduction_percentage": 0.0
            }
            
        _setup_nltk_morphology()
        import nltk
        from nltk.stem import PorterStemmer, WordNetLemmatizer
        
        stemmer = PorterStemmer()
        lemmatizer = WordNetLemmatizer()
        
        # 1. POS Tag the tokens
        pos_tagged_tokens = nltk.pos_tag(tokens)
        
        stemmed_tokens = []
        lemmatized_tokens = []
        morphology_pairs = []
        
        # We track unique values for metrics
        original_vocab = set()
        stem_vocab = set()
        lemma_vocab = set()
        
        # 2. Process each token
        for token, tag in pos_tagged_tokens:
            original_vocab.add(token)
            
            # Stemming
            stem = stemmer.stem(token)
            stemmed_tokens.append(stem)
            stem_vocab.add(stem)
            
            # Lemmatization (POS-aware)
            wn_pos = _get_wordnet_pos(tag)
            
            # Fix for isolated 'better' which is often tagged as RBR (adverb) by default
            if token.lower() == 'better' and wn_pos == 'r':
                wn_pos = 'a'
                
            lemma = lemmatizer.lemmatize(token, pos=wn_pos)
            lemmatized_tokens.append(lemma)
            lemma_vocab.add(lemma)
            
            # Explainability
            stem_exp = _generate_stem_explanation(token, stem)
            lemma_exp = _generate_lemma_explanation(token, lemma, wn_pos)
            
            morphology_pairs.append({
                "token": token,
                "pos_tag": tag,
                "wordnet_pos": wn_pos,
                "stem": stem,
                "lemma": lemma,
                "stem_explanation": stem_exp,
                "lemma_explanation": lemma_exp
            })
            
        # 3. Calculate metrics
        original_vocab_size = len(original_vocab)
        stemmed_vocab_size = len(stem_vocab)
        lemmatized_vocab_size = len(lemma_vocab)
        
        # Reduction relative to original vocabulary (not token count)
        if original_vocab_size > 0:
            vocab_reduction = ((original_vocab_size - lemmatized_vocab_size) / original_vocab_size) * 100
        else:
            vocab_reduction = 0.0
            
        return {
            "stemmed_tokens": stemmed_tokens,
            "lemmatized_tokens": lemmatized_tokens,
            "morphology_pairs": morphology_pairs,
            "unique_stems": stemmed_vocab_size,
            "unique_lemmas": lemmatized_vocab_size,
            "stem_count": len(stemmed_tokens),
            "lemma_count": len(lemmatized_tokens),
            "original_vocabulary_size": original_vocab_size,
            "stemmed_vocabulary_size": stemmed_vocab_size,
            "lemmatized_vocabulary_size": lemmatized_vocab_size,
            "vocabulary_reduction_percentage": round(vocab_reduction, 2)
        }
