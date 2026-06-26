"""
scripts/verify_pragmatic.py
Phase 8 Pragmatics & Discourse Intelligence Engine - Advanced Verification Script

Tests:
  - Coreference
  - Intent Classification
  - Discourse Detection
  - Context Tracking
  - Entity Timeline
  - Explanations & Confidences
"""

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pragmatic_service import PragmaticService


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
    print("PRAGMATIC & DISCOURSE ENGINE - ADVANCED VERIFICATION (Phase 8)")
    hr()

    # Test document
    sentences = [
        "John bought a laptop.",
        "He loves it because it is fast.",
        "However, he wishes it had more storage."
    ]
    
    # Mock tokens and POS tags for the test document
    tokens = ["John", "bought", "a", "laptop", "He", "loves", "it", "because", "it", "is", "fast", "However", "he", "wishes", "it", "had", "more", "storage"]
    syntax_data = {
        "pos_tags": [
            ("John", "NNP"), ("bought", "VBD"), ("a", "DT"), ("laptop", "NN"),
            ("He", "PRP"), ("loves", "VBZ"), ("it", "PRP"), ("because", "IN"), ("it", "PRP"), ("is", "VBZ"), ("fast", "JJ"),
            ("However", "RB"), ("he", "PRP"), ("wishes", "VBZ"), ("it", "PRP"), ("had", "VBD"), ("more", "JJR"), ("storage", "NN")
        ]
    }
    
    # Mock semantic data (simulating output from Phase 7)
    semantic_data = {
        "wsd": [
            {"word": "storage", "sense": "the act of storing something", "reason": "Matched storage context.", "confidence": 0.8}
        ]
    }

    results = PragmaticService.run_analysis(sentences, tokens, syntax_data, semantic_data)
    all_pass = True

    # ── 1. Coreference ────────────────────────────────────────────────────
    hr("-")
    print("TEST 1: Coreference Resolution")
    hr("-")
    coref = results.get("coreference", [])
    ok_coref = check(len(coref) > 0, f"Found {len(coref)} coreferences.")
    if not ok_coref: all_pass = False
    
    # We expect 'He' -> John, and 'it' -> laptop (due to heuristic tracking)
    he_maps = [c for c in coref if c["pronoun"].lower() == "he"]
    it_maps = [c for c in coref if c["pronoun"].lower() == "it"]
    
    if he_maps:
        ok_he = check(he_maps[0]["resolved_to"] == "John", f"'he' resolved to '{he_maps[0]['resolved_to']}'", "John", he_maps[0]["resolved_to"])
        if not ok_he: all_pass = False
    if it_maps:
        ok_it = check(it_maps[0]["resolved_to"] == "laptop", f"'it' resolved to '{it_maps[0]['resolved_to']}'", "laptop", it_maps[0]["resolved_to"])
        if not ok_it: all_pass = False
    print()

    # ── 2. Discourse Relations ────────────────────────────────────────────
    hr("-")
    print("TEST 2: Discourse Analysis")
    hr("-")
    discourse = results.get("discourse_relations", [])
    ok_disc = check(len(discourse) >= 2, f"Found {len(discourse)} discourse markers.")
    if not ok_disc: all_pass = False
    
    has_because = any(d["marker"] == "because" and d["relation"] == "Cause" for d in discourse)
    has_however = any(d["marker"] == "however" and d["relation"] == "Contrast" for d in discourse)
    
    ok_cause = check(has_because, "Detected 'because' (Cause).")
    ok_contrast = check(has_however, "Detected 'however' (Contrast).")
    
    if not (ok_cause and ok_contrast): all_pass = False
    print()

    # ── 3. Intent Classification ──────────────────────────────────────────
    hr("-")
    print("TEST 3: Intent Classification")
    hr("-")
    intents = results.get("intent_classification", [])
    ok_int = check(len(intents) == 3, f"Classified intents for {len(intents)} sentences.")
    if not ok_int: all_pass = False
    
    # "However, he wishes..." should be Opinion
    has_opinion = any(i["intent"] == "Opinion" for i in intents)
    ok_op = check(has_opinion, "Detected 'Opinion' intent in 'wishes' sentence.")
    if not ok_op: all_pass = False
    print()

    # ── 4. Context Tracking ───────────────────────────────────────────────
    hr("-")
    print("TEST 4: Context Tracking")
    hr("-")
    context = results.get("context_entities", [])
    ok_ctx = check(len(context) > 0, f"Found {len(context)} entity chains.")
    if not ok_ctx: all_pass = False
    for c in context:
        print(f"    Entity '{c['entity']}' chain: {c['chain']}")
    print()

    # ── 5. Entity Timeline ────────────────────────────────────────────────
    hr("-")
    print("TEST 5: Entity Timeline")
    hr("-")
    timeline = results.get("entity_timeline", [])
    ok_time = check(len(timeline) > 0, f"Extracted {len(timeline)} timeline events.")
    if not ok_time: all_pass = False
    for t in timeline:
        print(f"    Step {t['step']}: {t['entity']} -> {t['action']}")
    print()

    # ── 6. Ambiguity Resolution ───────────────────────────────────────────
    hr("-")
    print("TEST 6: Ambiguity Resolution (WSD reuse)")
    hr("-")
    ambig = results.get("ambiguity_resolution", [])
    ok_amb = check(len(ambig) > 0, f"Passed through {len(ambig)} semantic resolutions.")
    if not ok_amb: all_pass = False
    print()

    # ── 7. Summary & Confidences ──────────────────────────────────────────
    hr("-")
    print("TEST 7: Pragmatic Summary & Confidences")
    hr("-")
    summary = results.get("pragmatic_summary", {})
    conf = results.get("confidence_scores", {})
    
    ok_sum = check("primary_intent" in summary, f"Summary Primary Intent: {summary.get('primary_intent')}")
    ok_conf = check("average_confidence" in conf, f"Avg Confidence: {conf.get('average_confidence')}")
    if not (ok_sum and ok_conf): all_pass = False
    
    for k, v in conf.items():
        print(f"    {k}: {v}")
    print()

    # ── Final Report ──────────────────────────────────────────────────
    hr()
    if all_pass:
        print("VERIFICATION RESULT: PASS  —  All Phase 8 checks succeeded.")
    else:
        print("VERIFICATION RESULT: FAIL  —  One or more checks failed. See output above.")
    hr()
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    run_verification()
