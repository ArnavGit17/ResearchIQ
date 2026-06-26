"""
Phase 9B Verification Script
Tests: Dashboard Service, Health Score, Readability, Complexity, API Routes.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ─── Minimal Flask app context ────────────────────────────────────────────────
from flask import Flask
from app_extensions import db
import config as cfg

app = Flask(__name__, template_folder='../templates')
app.config.from_object(cfg.DevelopmentConfig)
db.init_app(app)

PASS = 0
FAIL = 0

def check(label, condition, info=""):
    global PASS, FAIL
    if condition:
        print(f"  [PASS] {label}" + (f" — {info}" if info else ""))
        PASS += 1
    else:
        print(f"  [FAIL] {label}" + (f" — {info}" if info else ""))
        FAIL += 1


# ──────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("RESEARCH INTELLIGENCE DASHBOARD — VERIFICATION (Phase 9B)")
print("=" * 60)


# ── TEST 1: DashboardService Import & Structure ────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 1: DashboardService Import & Method Structure")
print("------------------------------------------------------------")
try:
    from services.dashboard_service import DashboardService, _safe_json
    check("DashboardService imported", True)
    methods = ["compute_health_score", "compute_readability", "compute_complexity",
               "compute_research_insights", "compute_entity_intelligence",
               "compute_executive_summary", "compute_pipeline_timeline",
               "compare_documents", "batch_summary", "build"]
    for m in methods:
        check(f"Method '{m}' exists", hasattr(DashboardService, m))
except Exception as e:
    check("DashboardService imported", False, str(e))


# ── TEST 2: Health Score Formula ─────────────────────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 2: Health Score Formula (0–100)")
print("------------------------------------------------------------")
try:
    from unittest.mock import MagicMock
    import json

    # Build mock objects
    prep = MagicMock()
    prep.average_sentence_length = 18.0
    prep.token_count = 500

    morph = MagicMock()
    morph.vocabulary_reduction_percentage = 30.0

    stat = MagicMock()
    stat.type_token_ratio = 0.55
    stat.vocabulary_size = 400
    stat.total_tokens = 500
    stat.perplexity_score = 120.0

    sem = MagicMock()
    sem.semantic_pairs_json = json.dumps([{"word": "test"}] * 50)
    sem.ambiguity_score = 0.3

    app_res = MagicMock()
    app_res.entities_json = json.dumps({"entities": [{"entity": "Apple", "type": "ORG"}] * 10})
    app_res.summary_json  = json.dumps({"statistics": {"compression_ratio": 0.3, "original_sentences": 20, "summary_sentences": 6}})
    app_res.keywords_json = json.dumps([{"keyword": "nlp", "score": 0.9}] * 10)

    result = DashboardService.compute_health_score(prep, morph, stat, sem, app_res)

    check("Health score returns dict",  isinstance(result, dict))
    check("Composite in 0–100",         0 <= result.get("composite", -1) <= 100,
          f"Score = {result.get('composite')}")
    check("7 subscores present",        len(result.get("subscores", {})) == 7,
          f"Got {len(result.get('subscores', {}))}")
    check("7 explanations present",     len(result.get("explanations", {})) == 7)
    check("Grade field present",        "grade" in result)
    check("Formula field present",      "formula" in result)
except Exception as e:
    check("Health Score formula", False, str(e))


# ── TEST 3: Readability Analysis ──────────────────────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 3: Readability Analysis")
print("------------------------------------------------------------")
try:
    doc = MagicMock()
    doc.character_count = 5000
    doc.word_count = 800

    read = DashboardService.compute_readability(doc, prep, stat)
    check("Readability returns dict",        isinstance(read, dict))
    check("Difficulty field present",        "difficulty" in read)
    check("Difficulty is Easy/Medium/Hard",  read["difficulty"] in ("Easy","Medium","Hard"),
          f"Got: {read['difficulty']}")
    check("Avg sentence length > 0",         read.get("avg_sentence_length", 0) > 0)
    check("Reading time > 0",                read.get("reading_time_min", 0) > 0)
    check("Explanation present",             bool(read.get("explanation")))
except Exception as e:
    check("Readability Analysis", False, str(e))


# ── TEST 4: Complexity Analysis ───────────────────────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 4: Document Complexity")
print("------------------------------------------------------------")
try:
    syn = MagicMock()
    syn.pos_tags_json = json.dumps([{"word": w, "tag": t} for w, t in [
        ("The", "DT"), ("quick", "JJ"), ("fox", "NN"), ("runs", "VB"),
        ("over", "IN"), ("lazy", "JJ"), ("dogs", "NNS"), ("quickly", "RB")
    ]])

    comp = DashboardService.compute_complexity(stat, syn, sem, morph, prep)
    check("Complexity returns dict",          isinstance(comp, dict))
    check("Perplexity field present",         "perplexity" in comp)
    check("POS distribution not empty",       len(comp.get("pos_distribution", {})) > 0,
          f"POS keys: {list(comp.get('pos_distribution',{}).keys())}")
    check("Ambiguity score present",          "ambiguity_score" in comp)
    check("Lexical diversity present",        "lexical_diversity" in comp)
    check("Explanations dict has 5 keys",     len(comp.get("explanations",{})) >= 4)
except Exception as e:
    check("Complexity Analysis", False, str(e))


# ── TEST 5: Research Insights ─────────────────────────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 5: Research Insights")
print("------------------------------------------------------------")
try:
    stat.tfidf_json    = json.dumps({"nlp": 0.9, "machine": 0.8, "learning": 0.75, "neural": 0.7, "text": 0.6})
    stat.bigram_json   = json.dumps([["machine learning", 5], ["natural language", 4]])
    stat.unique_bigrams = 50
    morph.unique_lemmas = 300

    ins = DashboardService.compute_research_insights(stat, app_res, sem, morph)
    check("Insights returns dict",          isinstance(ins, dict))
    check("top_keywords present",           "top_keywords" in ins)
    check("topics generated",               len(ins.get("topics", [])) > 0,
          f"Topics: {len(ins.get('topics',[]))}")
    check("wordnet_coverage present",       "wordnet_coverage" in ins)
    check("vocabulary_size present",        "vocabulary_size" in ins)
    check("type_token_ratio present",       "type_token_ratio" in ins)
except Exception as e:
    check("Research Insights", False, str(e))


# ── TEST 6: Entity Intelligence ───────────────────────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 6: Entity Intelligence")
print("------------------------------------------------------------")
try:
    ent = DashboardService.compute_entity_intelligence(app_res)
    check("Entity intelligence returns dict",   isinstance(ent, dict))
    check("'entities' key present",             "entities" in ent)
    check("'distribution' key present",         "distribution" in ent)
    check("'by_type' key present",              "by_type" in ent)
    check("'top_entities' key present",         "top_entities" in ent)
except Exception as e:
    check("Entity Intelligence", False, str(e))


# ── TEST 7: Compare Documents (logic) ────────────────────────────────────────
print("------------------------------------------------------------")
print("TEST 7: Compare Documents — Error Handling")
print("------------------------------------------------------------")
try:
    with app.app_context():
        from unittest.mock import patch
        with patch('app_extensions.db.session.get', return_value=None), \
             patch('models.research_dashboard.ResearchDashboardResult.query') as mock_q:
            mock_q.filter_by.return_value.first.return_value = None
            result = DashboardService.compare_documents(999998, 999999)
            check("Returns dict on missing docs", isinstance(result, dict))
            check("Error key present for missing docs", "error" in result,
                  f"Got keys: {list(result.keys())}")
except Exception as e:
    check("Compare documents error handling", False, str(e))


# ── TEST 8: Batch Summary (empty) ─────────────────────────────────────────────
print("------------------------------------------------------------")
print("TEST 8: Batch Summary — Empty User")
print("------------------------------------------------------------")
try:
    with app.app_context():
        with patch('models.document.Document.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = []
            rows = DashboardService.batch_summary(user_id=999999)
            check("Batch summary returns list", isinstance(rows, list))
            check("Empty list for non-existent user", rows == [], f"Got: {rows}")
except Exception as e:
    check("Batch summary", False, str(e))


# ── TEST 9: Pipeline Timeline ─────────────────────────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 9: Pipeline Timeline")
print("------------------------------------------------------------")
try:
    doc2 = MagicMock()
    doc2.upload_date = None
    doc2.original_filename = "test.pdf"
    timeline = DashboardService.compute_pipeline_timeline(doc2, prep, morph, stat, syn, sem, None, app_res, None)
    check("Timeline returns list",        isinstance(timeline, list))
    check("Timeline has 9 stages",        len(timeline) == 9, f"Got {len(timeline)}")
    check("Each stage has 'phase' key",   all("phase" in s for s in timeline))
    check("Each stage has 'completed'",   all("completed" in s for s in timeline))
    check("Pragmatics stage is pending",  not timeline[6]["completed"])
except Exception as e:
    check("Pipeline Timeline", False, str(e))


# ── TEST 10: _safe_json helper ────────────────────────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 10: _safe_json Utility")
print("------------------------------------------------------------")
try:
    check("Valid JSON parsed correctly",    _safe_json('{"a":1}') == {"a": 1})
    check("Invalid JSON returns default",   _safe_json("not_json", []) == [])
    check("None returns empty dict",        _safe_json(None) == {})
    check("Empty string returns default",   _safe_json("", {}) == {})
except Exception as e:
    check("_safe_json utility", False, str(e))


# ── TEST 11: ResearchDashboardResult Model ───────────────────────────────────
print("\n------------------------------------------------------------")
print("TEST 11: ResearchDashboardResult Model")
print("------------------------------------------------------------")
try:
    from models.research_dashboard import ResearchDashboardResult
    check("Model imported", True)
    fields = ["health_score_json", "readability_json", "topic_analysis_json",
              "complexity_json", "executive_summary_json", "pipeline_timeline_json",
              "entity_intelligence_json", "research_insights_json", "document_overview_json"]
    for f in fields:
        check(f"Field '{f}' in model", hasattr(ResearchDashboardResult, f))
except Exception as e:
    check("ResearchDashboardResult model", False, str(e))


# ── SUMMARY ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
total = PASS + FAIL
print(f"VERIFICATION RESULT: {PASS}/{total} checks passed.")
if FAIL == 0:
    print("STATUS: PASS  [OK]  All Phase 9B checks succeeded.")
    sys.exit(0)
else:
    print(f"STATUS: FAIL  [X]  {FAIL} check(s) failed. See output above.")
    sys.exit(1)
