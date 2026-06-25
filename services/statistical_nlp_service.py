"""
Statistical NLP Service
=======================
Phase 5 – ResearchIQ

Provides:
  • Unigram / Bigram / Trigram frequency models
  • Term Frequency (TF)
  • TF-IDF (single-document approximation via IDF heuristic)
  • Unigram / Bigram / Trigram language model probabilities
  • Educational perplexity demonstration

Input:  list of lemmatised tokens from Phase 4 (MorphologyResult)
Output: structured dict ready for pipeline persistence
"""

import math
import logging
from collections import Counter
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# ── NLTK lazy initialisation ──────────────────────────────────────────────────
_NLTK_STAT_INITIALIZED = False


def _setup_nltk_stat():
    global _NLTK_STAT_INITIALIZED
    if _NLTK_STAT_INITIALIZED:
        return
    import nltk
    for pkg in ["stopwords"]:
        try:
            nltk.data.find(f"corpora/{pkg}")
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception as e:
                logger.warning(f"Failed to download NLTK {pkg}: {e}")
    _NLTK_STAT_INITIALIZED = True


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_stopwords() -> set:
    _setup_nltk_stat()
    from nltk.corpus import stopwords
    return set(stopwords.words("english"))


def _content_tokens(tokens: List[str]) -> List[str]:
    """Return lowercase alpha tokens stripped of stopwords."""
    sw = _get_stopwords()
    return [t.lower() for t in tokens if t.isalpha() and t.lower() not in sw and len(t) > 1]


def _top_n(counter: Counter, n: int) -> List[List]:
    """Return top-N entries as [[term, freq], ...]."""
    return [[k, v] for k, v in counter.most_common(n)]


# ── N-gram builders ───────────────────────────────────────────────────────────

def build_unigrams(tokens: List[str]) -> Counter:
    return Counter(tokens)


def build_bigrams(tokens: List[str]) -> Counter:
    return Counter(zip(tokens, tokens[1:]))


def build_trigrams(tokens: List[str]) -> Counter:
    return Counter(zip(tokens, tokens[1:], tokens[2:]))


# ── TF ────────────────────────────────────────────────────────────────────────

def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """
    Relative term frequency: TF(t) = count(t) / total_tokens
    """
    total = len(tokens)
    if total == 0:
        return {}
    counts = Counter(tokens)
    return {term: round(count / total, 6) for term, count in counts.items()}


# ── TF-IDF (single-document IDF heuristic) ───────────────────────────────────

def compute_tfidf(tokens: List[str], sentences: List[str]) -> Dict[str, float]:
    """
    IDF = log( (1 + N) / (1 + df(t)) ) + 1   (sklearn smooth variant)
    where N = number of sentences used as pseudo-documents.
    """
    if not tokens or not sentences:
        return {}

    # Treat each sentence as a mini-document
    N = len(sentences)
    sent_tokens = [set(s.lower().split()) for s in sentences]

    tf = compute_tf(tokens)
    tfidf = {}
    for term, tf_val in tf.items():
        df = sum(1 for st in sent_tokens if term in st)
        idf = math.log((1 + N) / (1 + df)) + 1.0
        tfidf[term] = round(tf_val * idf, 6)
    return tfidf


# ── Language Model ────────────────────────────────────────────────────────────

class LanguageModelService:
    """
    Academic unigram / bigram / trigram language models with Laplace smoothing.
    """

    @staticmethod
    def build(tokens: List[str]) -> Dict[str, Any]:
        """Build raw count tables for all three orders."""
        ug = build_unigrams(tokens)
        bg = build_bigrams(tokens)
        tg = build_trigrams(tokens)
        V  = len(ug)         # vocabulary size for Laplace
        N  = len(tokens)
        return {"unigram": ug, "bigram": bg, "trigram": tg, "V": V, "N": N}

    @staticmethod
    def unigram_prob(term: str, ug: Counter, N: int, V: int) -> float:
        """P(w) = (count(w) + 1) / (N + V)  — Laplace smoothed"""
        return (ug.get(term, 0) + 1) / (N + V)

    @staticmethod
    def bigram_prob(w1: str, w2: str, ug: Counter, bg: Counter, V: int) -> float:
        """P(w2|w1) = (count(w1,w2) + 1) / (count(w1) + V)"""
        return (bg.get((w1, w2), 0) + 1) / (ug.get(w1, 0) + V)

    @staticmethod
    def trigram_prob(w1: str, w2: str, w3: str, bg: Counter, tg: Counter, V: int) -> float:
        """P(w3|w1,w2) = (count(w1,w2,w3) + 1) / (count(w1,w2) + V)"""
        return (tg.get((w1, w2, w3), 0) + 1) / (bg.get((w1, w2), 0) + V)

    @classmethod
    def compute_sample(cls, model: Dict, sample_tokens: List[str]) -> Dict[str, Any]:
        """
        Calculate per-token probabilities for a sample sentence under all three models.
        Returns a structured dict for dashboard display.
        """
        ug, bg, tg = model["unigram"], model["bigram"], model["trigram"]
        V, N       = model["V"], model["N"]

        result = {
            "sentence":      " ".join(sample_tokens),
            "tokens":        sample_tokens,
            "unigram_probs": {},
            "bigram_probs":  {},
            "trigram_probs": {},
        }

        for i, w in enumerate(sample_tokens):
            p_ug = cls.unigram_prob(w, ug, N, V)
            result["unigram_probs"][w] = round(p_ug, 8)

            if i >= 1:
                p_bg = cls.bigram_prob(sample_tokens[i-1], w, ug, bg, V)
                result["bigram_probs"][f"{sample_tokens[i-1]} {w}"] = round(p_bg, 8)

            if i >= 2:
                p_tg = cls.trigram_prob(sample_tokens[i-2], sample_tokens[i-1], w, bg, tg, V)
                result["trigram_probs"][f"{sample_tokens[i-2]} {sample_tokens[i-1]} {w}"] = round(p_tg, 8)

        return result


# ── Perplexity ────────────────────────────────────────────────────────────────

class PerplexityService:
    """
    Computes perplexity of a sample sentence under a unigram language model.

    PP(W) = exp( -1/N  *  Σ log P(w_i) )
    """

    @staticmethod
    def compute(sample_tokens: List[str], model: Dict) -> Dict[str, Any]:
        ug, V, N = model["unigram"], model["V"], model["N"]
        n = len(sample_tokens)
        if n == 0:
            return {"perplexity": 0.0, "log_probs": [], "formula": "", "interpretation": ""}

        log_probs = []
        detail    = []
        for w in sample_tokens:
            p = LanguageModelService.unigram_prob(w, ug, N, V)
            lp = math.log(p)
            log_probs.append(round(lp, 6))
            detail.append({"token": w, "prob": round(p, 8), "log_prob": round(lp, 6)})

        avg_log  = sum(log_probs) / n
        perplexity = round(math.exp(-avg_log), 4)

        formula = (
            f"PP(W) = exp( −(1/{n}) × ({' + '.join(str(lp) for lp in log_probs[:5])}"
            + (" + ..." if n > 5 else "")
            + f") ) = exp({round(-avg_log, 6)}) = {perplexity}"
        )

        if perplexity < 50:
            interpretation = "Very low perplexity — model fits this text extremely well."
        elif perplexity < 200:
            interpretation = "Moderate perplexity — model has reasonable predictive power."
        elif perplexity < 1000:
            interpretation = "High perplexity — model is uncertain about many tokens."
        else:
            interpretation = "Very high perplexity — model is nearly random for this text."

        return {
            "sentence":       " ".join(sample_tokens),
            "token_detail":   detail,
            "log_probs":      log_probs,
            "avg_log_prob":   round(avg_log, 6),
            "perplexity":     perplexity,
            "formula":        formula,
            "interpretation": interpretation,
        }


# ── Main service entry point ──────────────────────────────────────────────────

class StatisticalNLPService:
    """
    Orchestrates the full Phase 5 statistical analysis pipeline.

    Input:  lemmatised_tokens (List[str])  from MorphologyResult
            sentences         (List[str])  from PreprocessingResult
    Output: structured results dict
    """

    TOP_UNIGRAMS = 200
    TOP_BIGRAMS  = 100
    TOP_TRIGRAMS = 50
    TOP_TF       = 100
    TOP_TFIDF    = 100
    SAMPLE_LEN   = 10   # tokens for language model / perplexity demo

    @classmethod
    def run_analysis(cls, lemmatised_tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        if not lemmatised_tokens:
            return cls._empty_result()

        # 1. Filter content tokens (no stopwords, alpha-only)
        content = _content_tokens(lemmatised_tokens)

        if not content:
            return cls._empty_result()

        # 2. N-grams
        ug_counter = build_unigrams(content)
        bg_counter = build_bigrams(content)
        tg_counter = build_trigrams(content)

        top_ug = _top_n(ug_counter, cls.TOP_UNIGRAMS)
        # Serialise bigram/trigram keys as strings for JSON
        top_bg = [[f"{a} {b}", cnt] for (a, b), cnt in bg_counter.most_common(cls.TOP_BIGRAMS)]
        top_tg = [[f"{a} {b} {c}", cnt] for (a, b, c), cnt in tg_counter.most_common(cls.TOP_TRIGRAMS)]

        # 3. TF / TF-IDF (on content tokens, using sentences as pseudo-docs)
        tf     = compute_tf(content)
        tfidf  = compute_tfidf(content, sentences)

        top_tf    = sorted(tf.items(),    key=lambda x: x[1], reverse=True)[:cls.TOP_TF]
        top_tfidf = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)[:cls.TOP_TFIDF]

        # 4. Language model
        lm_model   = LanguageModelService.build(content)
        # Pick most frequent tokens as a natural sample sentence
        most_common_terms = [t for t, _ in ug_counter.most_common(cls.SAMPLE_LEN * 3)]
        sample_tokens     = most_common_terms[:cls.SAMPLE_LEN]
        lm_sample         = LanguageModelService.compute_sample(lm_model, sample_tokens)

        # 5. Perplexity
        perp_detail = PerplexityService.compute(sample_tokens, lm_model)

        # 6. Corpus stats
        V               = len(ug_counter)
        total           = len(content)
        ttr             = round(V / total, 4) if total else 0.0
        unique_bigrams  = len(bg_counter)
        unique_trigrams = len(tg_counter)

        return {
            "unigrams":             top_ug,
            "bigrams":              top_bg,
            "trigrams":             top_tg,
            "tf":                   [[t, s] for t, s in top_tf],
            "tfidf":                [[t, s] for t, s in top_tfidf],
            "vocabulary_size":      V,
            "total_tokens":         total,
            "unique_bigrams":       unique_bigrams,
            "unique_trigrams":      unique_trigrams,
            "type_token_ratio":     ttr,
            "language_model":       lm_sample,
            "perplexity_detail":    perp_detail,
            "perplexity_score":     perp_detail["perplexity"],
        }

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            "unigrams": [], "bigrams": [], "trigrams": [],
            "tf": [], "tfidf": [],
            "vocabulary_size": 0, "total_tokens": 0,
            "unique_bigrams": 0, "unique_trigrams": 0,
            "type_token_ratio": 0.0,
            "language_model": {}, "perplexity_detail": {},
            "perplexity_score": 0.0,
        }
