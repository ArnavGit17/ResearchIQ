"""
verify_statistical.py
Automated verification for Phase 5 – Statistical NLP Engine
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.statistical_nlp_service import (
    StatisticalNLPService,
    LanguageModelService,
    PerplexityService,
    build_unigrams,
    build_bigrams,
    build_trigrams,
    compute_tf,
    compute_tfidf,
)

PASS = "PASS"
FAIL = "FAIL"

print("=" * 60)
print("STATISTICAL NLP ENGINE - VERIFICATION")
print("=" * 60)

# ── Sample corpus ─────────────────────────────────────────────
TOKENS = (
    "natural language processing enables computers understand text "
    "language model compute probability word sequence statistical "
    "natural language text corpus analysis term frequency document "
    "bigram trigram language model perplexity score information "
    "research analysis document corpus natural language".split()
)
SENTENCES = [
    "Natural language processing enables computers to understand text.",
    "A language model computes the probability of a word sequence.",
    "Statistical NLP uses term frequency and TF-IDF for analysis.",
    "Bigram and trigram models capture local word context.",
    "Perplexity measures how well a language model predicts text.",
]

results = StatisticalNLPService.run_analysis(TOKENS, SENTENCES)

# ── 1. Unigrams ───────────────────────────────────────────────
print("\n1. Verifying Unigrams:")
ug = results["unigrams"]
assert len(ug) > 0, "No unigrams returned"
top_term, top_freq = ug[0]
print(f"   Top unigram: [{top_term}] -> freq={top_freq}  {PASS}")
assert isinstance(top_freq, int) and top_freq > 0
print(f"   Unigram count: {len(ug)}  {PASS}")

# ── 2. Bigrams ────────────────────────────────────────────────
print("\n2. Verifying Bigrams:")
bg = results["bigrams"]
assert len(bg) > 0, "No bigrams returned"
bg_phrase, bg_cnt = bg[0]
assert " " in bg_phrase, "Bigram key must be two words separated by space"
print(f"   Top bigram: [{bg_phrase}] -> count={bg_cnt}  {PASS}")
print(f"   Unique bigrams stored: {results['unique_bigrams']}  {PASS}")

# ── 3. Trigrams ───────────────────────────────────────────────
print("\n3. Verifying Trigrams:")
tg = results["trigrams"]
assert len(tg) > 0, "No trigrams returned"
tg_phrase, tg_cnt = tg[0]
assert tg_phrase.count(" ") == 2, "Trigram key must be 3 words"
print(f"   Top trigram: [{tg_phrase}] -> count={tg_cnt}  {PASS}")
print(f"   Unique trigrams stored: {results['unique_trigrams']}  {PASS}")

# ── 4. Term Frequency ─────────────────────────────────────────
print("\n4. Verifying Term Frequency (TF):")
tf = results["tf"]
assert len(tf) > 0, "No TF entries returned"
tf_term, tf_score = tf[0]
assert 0.0 < tf_score <= 1.0, f"TF score out of range: {tf_score}"
print(f"   Top TF: [{tf_term}] -> TF={tf_score:.6f}  {PASS}")
all_scores = [s for _, s in tf]
assert all_scores == sorted(all_scores, reverse=True), "TF list not sorted descending"
print(f"   TF list sorted descending  {PASS}")

# ── 5. TF-IDF ────────────────────────────────────────────────
print("\n5. Verifying TF-IDF:")
tfidf = results["tfidf"]
assert len(tfidf) > 0, "No TF-IDF entries returned"
tfidf_term, tfidf_score = tfidf[0]
assert tfidf_score > 0, f"TF-IDF score should be positive, got {tfidf_score}"
print(f"   Top TF-IDF: [{tfidf_term}] -> score={tfidf_score:.6f}  {PASS}")

# ── 6. Vocabulary stats ───────────────────────────────────────
print("\n6. Verifying Vocabulary Statistics:")
vocab  = results["vocabulary_size"]
tokens = results["total_tokens"]
ttr    = results["type_token_ratio"]
assert vocab > 0,          "Vocabulary size must be > 0"
assert tokens > 0,         "Total tokens must be > 0"
assert 0 < ttr <= 1.0,     f"TTR out of range: {ttr}"
print(f"   Vocabulary size : {vocab}   {PASS}")
print(f"   Total tokens    : {tokens}  {PASS}")
print(f"   Type-Token Ratio: {ttr}     {PASS}")

# ── 7. Language Model ─────────────────────────────────────────
print("\n7. Verifying Language Model:")
lm = results["language_model"]
assert "sentence"      in lm, "Missing 'sentence' in LM output"
assert "unigram_probs" in lm, "Missing 'unigram_probs'"
assert "bigram_probs"  in lm, "Missing 'bigram_probs'"
assert "trigram_probs" in lm, "Missing 'trigram_probs'"
assert len(lm["unigram_probs"]) > 0, "No unigram probabilities"
sample_prob = list(lm["unigram_probs"].values())[0]
assert 0 < sample_prob < 1, f"Unigram prob out of range: {sample_prob}"
print(f"   Sample sentence : {lm['sentence']}  {PASS}")
print(f"   Unigram probs   : {len(lm['unigram_probs'])} entries  {PASS}")
print(f"   Bigram probs    : {len(lm['bigram_probs'])} entries  {PASS}")
print(f"   Trigram probs   : {len(lm['trigram_probs'])} entries  {PASS}")
print(f"   Sample P(w)     : {sample_prob:.8f}  {PASS}")

# ── 8. Perplexity ─────────────────────────────────────────────
print("\n8. Verifying Perplexity:")
perp = results["perplexity_detail"]
score = results["perplexity_score"]
assert score > 0,                         f"Perplexity must be positive, got {score}"
assert "formula"        in perp,          "Missing 'formula' in perplexity detail"
assert "interpretation" in perp,          "Missing 'interpretation'"
assert "token_detail"   in perp,          "Missing 'token_detail'"
assert len(perp["token_detail"]) > 0,     "No token detail entries"
tok0 = perp["token_detail"][0]
assert "token"    in tok0 and "prob" in tok0 and "log_prob" in tok0
print(f"   Perplexity score      : {score}  {PASS}")
print(f"   Formula present       : {PASS}")
print(f"   Interpretation present: {PASS}")
print(f"   Token breakdown count : {len(perp['token_detail'])}  {PASS}")
print(f"   Sample token detail   : {tok0['token']} -> P={tok0['prob']:.6f}  {PASS}")

# ── Summary ───────────────────────────────────────────────────
print()
print("=" * 60)
print("VERIFICATION: PASS")
print("=" * 60)
print()
print("Phase 5 – Statistical NLP Engine is fully operational.")
print("  Unigrams, Bigrams, Trigrams: OK")
print("  TF, TF-IDF               : OK")
print("  Language Model (3 orders) : OK")
print("  Perplexity Demonstration  : OK")
print("  Vocabulary Statistics     : OK")
