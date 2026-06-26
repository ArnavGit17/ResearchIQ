"""
Semantic Analysis Service  –  Phase 7
======================================
Provides:
  • WordNet synonym / antonym / hypernym / hyponym extraction
  • path_similarity & wup_similarity scoring
  • Lesk-based Word Sense Disambiguation with explainability
  • Ambiguity scoring (average WordNet senses per content word)
  • WordNet coverage statistics (future-phase reuse hook)

All public return dicts are stable; downstream phases must not break if new
keys are added.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any, Dict, List, Tuple

import nltk
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk

logger = logging.getLogger(__name__)

# ── NLTK resource bootstrap ────────────────────────────────────────────────────
_REQUIRED_CORPORA    = ["wordnet", "omw-1.4"]
_REQUIRED_TOKENIZERS = ["punkt", "punkt_tab"]

for _res in _REQUIRED_CORPORA:
    try:
        nltk.data.find(f"corpora/{_res}")
    except LookupError:
        logger.info("Downloading NLTK corpus: %s", _res)
        nltk.download(_res, quiet=True)

for _res in _REQUIRED_TOKENIZERS:
    try:
        nltk.data.find(f"tokenizers/{_res}")
    except LookupError:
        logger.info("Downloading NLTK tokenizer: %s", _res)
        nltk.download(_res, quiet=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _safe_tokenize(text: str) -> List[str]:
    """Tokenize with graceful fallback."""
    try:
        return nltk.word_tokenize(text)
    except Exception:
        return text.split()


def _strength_label(score: float) -> str:
    """Map a [0,1] similarity score to a human-readable label."""
    if score >= 0.85:
        return "Near-Identical"
    if score >= 0.70:
        return "Very High"
    if score >= 0.55:
        return "High"
    if score >= 0.40:
        return "Moderate"
    if score >= 0.25:
        return "Low"
    return "Very Low"


# ── Core service ───────────────────────────────────────────────────────────────

class SemanticService:
    """Stateless collection of WordNet-powered NLP utilities."""

    # ── 1. Word Relations ──────────────────────────────────────────────────────

    @staticmethod
    def get_word_relations(word: str) -> Dict[str, Any]:
        """
        Return synonyms, antonyms, hypernyms, hyponyms, and sense count
        for *word* via WordNet.

        Returns
        -------
        {
          "synonyms":   List[str],
          "antonyms":   List[str],
          "hypernyms":  List[str],
          "hyponyms":   List[str],
          "num_senses": int,
          "in_wordnet": bool,
        }
        """
        synonyms: set[str] = set()
        antonyms: set[str] = set()
        hypernyms: set[str] = set()
        hyponyms: set[str] = set()

        synsets = wn.synsets(word)
        for syn in synsets:
            for lemma in syn.lemmas():
                clean = lemma.name().replace("_", " ")
                synonyms.add(clean)
                for ant in lemma.antonyms():
                    antonyms.add(ant.name().replace("_", " "))

            for hyper in syn.hypernyms():
                for lm in hyper.lemmas():
                    hypernyms.add(lm.name().replace("_", " "))

            for hypo in syn.hyponyms():
                for lm in hypo.lemmas():
                    hyponyms.add(lm.name().replace("_", " "))

        # Remove the word itself from synonyms
        synonyms.discard(word)
        synonyms.discard(word.replace(" ", "_"))

        return {
            "synonyms":   sorted(synonyms)[:20],
            "antonyms":   sorted(antonyms)[:10],
            "hypernyms":  sorted(hypernyms)[:15],
            "hyponyms":   sorted(hyponyms)[:20],
            "num_senses": len(synsets),
            "in_wordnet": len(synsets) > 0,
        }

    # ── 2. Semantic Similarity ─────────────────────────────────────────────────

    @staticmethod
    def calculate_similarities(words: List[str]) -> List[Dict[str, Any]]:
        """
        Calculate path_similarity and wup_similarity between consecutive
        unique content words.

        Returns a list of dicts:
        {
          "word1": str, "word2": str,
          "path_similarity": float,
          "wup_similarity": float,
          "strength": str,   # human-readable label
        }
        """
        similarities: List[Dict[str, Any]] = []
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: List[str] = []
        for w in words:
            if w not in seen:
                seen.add(w)
                unique.append(w)

        valid = [w for w in unique if len(w) >= 3][:25]

        for i in range(len(valid) - 1):
            w1, w2 = valid[i], valid[i + 1]
            s1 = wn.synsets(w1)
            s2 = wn.synsets(w2)
            if not (s1 and s2):
                continue
            syn1, syn2 = s1[0], s2[0]
            path_sim = syn1.path_similarity(syn2)
            wup_sim  = syn1.wup_similarity(syn2)
            if path_sim is None or wup_sim is None:
                continue
            similarities.append({
                "word1":            w1,
                "word2":            w2,
                "path_similarity":  round(path_sim, 4),
                "wup_similarity":   round(wup_sim, 4),
                "strength":         _strength_label(wup_sim),
            })
        return similarities

    # ── 3. Word Sense Disambiguation (Lesk + explainability) ──────────────────

    @staticmethod
    def perform_wsd(
        sentences: List[str],
        target_words: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Run Lesk WSD on *target_words* within *sentences*.

        Returns a list of dicts:
        {
          "word": str,
          "context": str,
          "sense": str,          # synset definition (title-cased)
          "synset_name": str,    # e.g. "bank.n.01"
          "pos": str,            # part-of-speech
          "reason": str,         # explainability: nearby context clues
        }
        """
        results: List[Dict[str, Any]] = []
        seen_pairs: set[Tuple[str, str]] = set()

        for sent in sentences[:15]:          # performance cap
            tokens = _safe_tokenize(sent)
            lower_tokens = [t.lower() for t in tokens]

            for word in target_words:
                pair = (word, sent[:60])
                if pair in seen_pairs:
                    continue

                word_lower = word.lower()
                if word_lower not in lower_tokens:
                    continue

                synset = lesk(lower_tokens, word_lower)
                if synset is None:
                    continue

                seen_pairs.add(pair)

                # Collect context clue words (not the target, not stopwords)
                clues = [
                    t for t in lower_tokens
                    if t != word_lower and len(t) > 3 and t.isalpha()
                ][:5]

                pos_map = {"n": "Noun", "v": "Verb", "a": "Adjective",
                           "s": "Adjective (Satellite)", "r": "Adverb"}
                pos_label = pos_map.get(synset.pos(), synset.pos().upper())

                sense_def = synset.definition()

                # Build a domain hint from synset lexname
                lexname = synset.lexname()          # e.g. "noun.cognition"
                domain_hint = lexname.split(".")[-1].replace("_", " ").title() \
                    if lexname else "General"

                reason = (
                    f"Context words ({', '.join(repr(c) for c in clues)}) "
                    f"align with the '{domain_hint}' domain of this synset. "
                    f"Lesk algorithm selected synset '{synset.name()}' "
                    f"because its definition overlaps most with the surrounding context."
                )

                results.append({
                    "word":        word,
                    "context":     sent.strip(),
                    "sense":       sense_def.capitalize(),
                    "synset_name": synset.name(),
                    "pos":         pos_label,
                    "reason":      reason,
                })

        return results

    # ── 4. WordNet Coverage Statistics ────────────────────────────────────────

    @staticmethod
    def wordnet_coverage_stats(words: List[str]) -> Dict[str, Any]:
        """
        Return coverage stats for *words* in WordNet.
        Reusable by future phases (Semantic Search, QA).

        Returns
        -------
        {
          "total_words":      int,
          "in_wordnet":       int,
          "not_in_wordnet":   int,
          "coverage_pct":     float,
          "avg_senses":       float,
          "max_senses_word":  str,
          "max_senses_count": int,
        }
        """
        in_wn = 0
        total_senses = 0
        max_senses = 0
        max_word = ""

        for w in words:
            ss = wn.synsets(w)
            if ss:
                in_wn += 1
                total_senses += len(ss)
                if len(ss) > max_senses:
                    max_senses = len(ss)
                    max_word = w

        n = len(words) or 1
        return {
            "total_words":      len(words),
            "in_wordnet":       in_wn,
            "not_in_wordnet":   len(words) - in_wn,
            "coverage_pct":     round(in_wn / n * 100, 2),
            "avg_senses":       round(total_senses / max(in_wn, 1), 2),
            "max_senses_word":  max_word,
            "max_senses_count": max_senses,
        }

    # ── 5. Master pipeline ────────────────────────────────────────────────────

    @staticmethod
    def run_analysis(
        sentences: List[str],
        tokens: List[str],
    ) -> Dict[str, Any]:
        """
        Full Phase 7 analysis.  Accepts lemmatised tokens from Phase 4
        and raw sentences from Phase 3.  Does NOT re-run earlier phases.

        Returns a stable dict consumed by NLPPipeline.run_semantic_analysis().
        Keys:
          synonyms, antonyms, hypernyms, hyponyms,
          semantic_pairs, semantic_similarity,
          word_senses, ambiguous_words,
          ambiguity_score, wordnet_coverage
        """
        logger.info("SemanticService.run_analysis: start")

        # ── Select top N content words ────────────────────────────────────────
        content_tokens = [
            t.lower() for t in tokens
            if len(t) > 3 and t.isalpha()
        ]
        freq = Counter(content_tokens)
        top_words: List[str] = [w for w, _ in freq.most_common(40)]

        synonyms_map:  Dict[str, List[str]] = {}
        antonyms_map:  Dict[str, List[str]] = {}
        hypernyms_map: Dict[str, List[str]] = {}
        hyponyms_map:  Dict[str, List[str]] = {}
        semantic_pairs: List[Dict[str, Any]] = []
        ambiguous_words: List[Dict[str, Any]] = []

        total_senses   = 0
        words_with_syn = 0

        for word in top_words:
            rel = SemanticService.get_word_relations(word)

            if rel["synonyms"]:
                synonyms_map[word]  = rel["synonyms"]
            if rel["antonyms"]:
                antonyms_map[word]  = rel["antonyms"]
            if rel["hypernyms"]:
                hypernyms_map[word] = rel["hypernyms"]
            if rel["hyponyms"]:
                hyponyms_map[word]  = rel["hyponyms"]

            semantic_pairs.append({
                "word":      word,
                "synonyms":  rel["synonyms"],
                "antonyms":  rel["antonyms"],
                "hypernyms": rel["hypernyms"],
                "hyponyms":  rel["hyponyms"],
            })

            senses = rel["num_senses"]
            if senses > 0:
                total_senses   += senses
                words_with_syn += 1
                if senses > 2:
                    ambiguous_words.append({"word": word, "senses": senses})

        ambiguity_score = (
            round(total_senses / words_with_syn, 4)
            if words_with_syn > 0 else 0.0
        )

        # Sort ambiguous words by number of senses (desc) and cap
        ambiguous_words = sorted(
            ambiguous_words, key=lambda x: x["senses"], reverse=True
        )[:15]

        # WSD targets: top ambiguous words
        wsd_targets = [item["word"] for item in ambiguous_words[:8]]
        wsd_results = SemanticService.perform_wsd(sentences, wsd_targets)

        # Similarity
        similarities = SemanticService.calculate_similarities(top_words)

        # WordNet coverage
        coverage = SemanticService.wordnet_coverage_stats(top_words)

        logger.info(
            "SemanticService.run_analysis: done — %d pairs, %d sims, %d WSD",
            len(semantic_pairs), len(similarities), len(wsd_results),
        )

        return {
            "synonyms":          synonyms_map,
            "antonyms":          antonyms_map,
            "hypernyms":         hypernyms_map,
            "hyponyms":          hyponyms_map,
            "semantic_pairs":    semantic_pairs,
            "semantic_similarity": similarities,
            "word_senses":       wsd_results,
            "ambiguous_words":   ambiguous_words,
            "ambiguity_score":   ambiguity_score,
            "wordnet_coverage":  coverage,
        }
