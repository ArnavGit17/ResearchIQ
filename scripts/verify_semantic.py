"""
scripts/verify_semantic.py
Phase 7 Semantic Analysis Engine - Advanced Verification Script

Tests:
  - WordNet synonyms, antonyms, hypernyms, hyponyms
  - Semantic similarity (path + WUP)
  - Word Sense Disambiguation (Lesk)
  - Ambiguity scoring
  - WordNet coverage statistics
  - API structure validation

Words tested: car, vehicle, bank, good, happy, light, match, bat
"""

import os
import sys
import json

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from services.semantic_service import SemanticService


def hr(char="=", width=60):
    print(char * width)


def check(condition, label, expected=None, got=None):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}", end="")
    if not condition and expected is not None:
        print(f" | Expected: {expected!r}  Got: {got!r}", end="")
    print()
    return condition


def run_verification():
    hr()
    print("SEMANTIC ANALYSIS ENGINE - ADVANCED VERIFICATION (Phase 7)")
    hr()

    app = create_app("testing")
    with app.app_context():

        test_words = ["car", "vehicle", "bank", "good", "happy", "light", "match", "bat"]
        all_pass = True

        # ── 1. Synonyms ────────────────────────────────────────────────────
        hr("-")
        print("TEST 1: Synonyms")
        hr("-")
        syn_words_found = 0
        for w in test_words:
            rel = SemanticService.get_word_relations(w)
            ok = len(rel["synonyms"]) > 0
            p = check(ok, f"{w} -> synonyms: {rel['synonyms'][:3]}")
            if ok: syn_words_found += 1
            if not p: all_pass = False
        print(f"  Synonym coverage: {syn_words_found}/{len(test_words)} words\n")

        # ── 2. Antonyms ────────────────────────────────────────────────────
        hr("-")
        print("TEST 2: Antonyms")
        hr("-")
        ant_test = ["good", "happy", "light"]
        for w in ant_test:
            rel = SemanticService.get_word_relations(w)
            ok = len(rel["antonyms"]) > 0
            p = check(ok, f"{w} -> antonyms: {rel['antonyms'][:3]}")
            if not p: all_pass = False
        print()

        # ── 3. Hypernyms ───────────────────────────────────────────────────
        hr("-")
        print("TEST 3: Hypernyms")
        hr("-")
        for w in ["car", "bank", "good"]:
            rel = SemanticService.get_word_relations(w)
            ok = len(rel["hypernyms"]) > 0
            p = check(ok, f"{w} -> hypernyms: {rel['hypernyms'][:3]}")
            if not p: all_pass = False
        print()

        # ── 4. Hyponyms ────────────────────────────────────────────────────
        hr("-")
        print("TEST 4: Hyponyms")
        hr("-")
        for w in ["vehicle", "light"]:
            rel = SemanticService.get_word_relations(w)
            ok = len(rel["hyponyms"]) > 0
            p = check(ok, f"{w} -> hyponyms: {rel['hyponyms'][:3]}")
            if not p: all_pass = False
        print()

        # ── 5. Semantic Similarity ─────────────────────────────────────────
        hr("-")
        print("TEST 5: Semantic Similarity (path + WUP)")
        hr("-")
        sims = SemanticService.calculate_similarities(["car", "automobile", "banana", "vehicle", "happy"])
        ok_count = check(len(sims) > 0, f"Similarity pairs computed: {len(sims)}")
        if not ok_count: all_pass = False

        for s in sims[:5]:
            print(f"    {s['word1']} <-> {s['word2']}  path={s['path_similarity']}  wup={s['wup_similarity']}  [{s['strength']}]")

        # Spot-check car/automobile should be high similarity
        car_auto = [s for s in sims if set([s["word1"],s["word2"]]) == {"car","automobile"}]
        if car_auto:
            ok_high = check(car_auto[0]["wup_similarity"] >= 0.7,
                            f"car<->automobile WUP is high ({car_auto[0]['wup_similarity']})")
            if not ok_high: all_pass = False
        print()

        # ── 6. WSD ────────────────────────────────────────────────────────
        hr("-")
        print("TEST 6: Word Sense Disambiguation (Lesk)")
        hr("-")
        test_sents = [
            "I deposited money in the bank yesterday.",
            "We sat on the river bank and fished.",
            "The light from the window was bright.",
            "I need to light a candle.",
        ]
        wsd_results = SemanticService.perform_wsd(test_sents, ["bank", "light"])
        ok_wsd = check(len(wsd_results) > 0, f"WSD produced {len(wsd_results)} result(s)")
        if not ok_wsd: all_pass = False
        for r in wsd_results:
            print(f"    Word={r['word']}  Sense={r['sense'][:60]}...")
            print(f"    Synset={r['synset_name']}  POS={r['pos']}")
            print(f"    Reason preview: {r['reason'][:80]}...")
            print()

        # ── 7. Ambiguity Score ─────────────────────────────────────────────
        hr("-")
        print("TEST 7: Ambiguity Analysis")
        hr("-")
        all_tokens = test_words + ["bank", "light", "match", "bat", "bat", "bank"]
        all_sents  = test_sents
        results = SemanticService.run_analysis(all_sents, all_tokens)

        ok_score = check(results["ambiguity_score"] > 0, f"Ambiguity score: {results['ambiguity_score']:.4f}")
        if not ok_score: all_pass = False

        ambig = results["ambiguous_words"]
        ok_amb = check(len(ambig) > 0, f"Ambiguous words found: {[a['word'] for a in ambig[:5]]}")
        if not ok_amb: all_pass = False
        print()

        # ── 8. WordNet Coverage ────────────────────────────────────────────
        hr("-")
        print("TEST 8: WordNet Coverage Statistics")
        hr("-")
        cov = SemanticService.wordnet_coverage_stats(test_words)
        ok_cov = check(cov["coverage_pct"] > 50,
                       f"Coverage {cov['coverage_pct']}% ({cov['in_wordnet']}/{cov['total_words']} words)")
        ok_avg = check(cov["avg_senses"] > 1, f"Avg senses: {cov['avg_senses']}")
        if not ok_cov or not ok_avg: all_pass = False
        print(f"    Max ambiguous word: '{cov['max_senses_word']}'  ({cov['max_senses_count']} senses)\n")

        # ── 9. Semantic Pairs reuse structure ─────────────────────────────
        hr("-")
        print("TEST 9: Semantic Pairs Storage (future-phase reuse)")
        hr("-")
        pairs = results["semantic_pairs"]
        ok_pairs = check(len(pairs) > 0, f"Semantic pairs generated: {len(pairs)}")
        if pairs:
            sample = pairs[0]
            ok_keys = check(all(k in sample for k in ["word","synonyms","antonyms","hypernyms","hyponyms"]),
                            "Semantic pair has all required keys")
            if not ok_keys: all_pass = False
        if not ok_pairs: all_pass = False
        print()

        # ── 10. JSON serialisation (for API/DB) ───────────────────────────
        hr("-")
        print("TEST 10: JSON Serialisation (API readiness)")
        hr("-")
        try:
            j = json.dumps(results)
            ok_json = check(len(j) > 100, f"Serialised to JSON ({len(j)} chars)")
        except Exception as e:
            ok_json = check(False, f"JSON serialisation FAILED: {e}")
        if not ok_json: all_pass = False
        print()

        # ── Final Report ──────────────────────────────────────────────────
        hr()
        if all_pass:
            print("VERIFICATION RESULT: PASS  —  All Phase 7 checks succeeded.")
        else:
            print("VERIFICATION RESULT: FAIL  —  One or more checks failed. See output above.")
        hr()
        sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    run_verification()
