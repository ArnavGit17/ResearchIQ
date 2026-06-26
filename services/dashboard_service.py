"""
Phase 9B: Dashboard Aggregation Service
Reads ALL phase outputs from the DB and computes research intelligence metrics.
NO NLP is re-run here — this is a pure read + compute layer.
"""

import json
import math
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app_extensions import db
from models.document import Document
from models.preprocessing import PreprocessingResult
from models.morphology import MorphologyResult
from models.statistical_nlp import StatisticalAnalysisResult
from models.syntax import SyntaxAnalysisResult
from models.semantic import SemanticAnalysisResult
from models.pragmatic import PragmaticAnalysisResult
from models.application import ApplicationAnalysisResult
from models.research_dashboard import ResearchDashboardResult

logger = logging.getLogger(__name__)


def _safe_json(val: Optional[str], default=None) -> Any:
    """Safely parse a JSON string; return default on failure."""
    if not val:
        return default if default is not None else {}
    try:
        return json.loads(val)
    except Exception:
        return default if default is not None else {}


class DashboardService:
    """Aggregates all NLP phase outputs into Research Intelligence metrics."""

    # ─────────────────────────────────────────────────────────────────────────
    # 1. DOCUMENT OVERVIEW
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_document_overview(doc: Document, prep: Optional[PreprocessingResult]) -> Dict:
        words = doc.word_count or (prep.token_count if prep else 0)
        sentences = doc.sentence_count or (prep.sentence_count if prep else 0)
        chars = doc.character_count or 0
        avg_wpm = 238  # average adult reading speed
        reading_time_min = round(words / avg_wpm, 1) if words else 0

        # Estimate pages (250 words/page typical)
        pages = max(1, round(words / 250))

        # Count which NLP modules are done
        modules_done = []
        phases = [
            ("Preprocessing", prep),
        ]

        completed_count = sum(1 for _, r in phases if r is not None)

        return {
            "filename": doc.original_filename,
            "file_type": doc.file_type.upper() if doc.file_type else "UNKNOWN",
            "file_size": doc.file_size_display,
            "upload_date": doc.upload_date.strftime("%B %d, %Y %H:%M") if doc.upload_date else "N/A",
            "words": words,
            "sentences": sentences,
            "characters": chars,
            "paragraphs": max(1, sentences // 4),  # rough estimate
            "pages": pages,
            "reading_time_min": reading_time_min,
            "avg_sentence_length": round(prep.average_sentence_length, 1) if prep else 0,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 2. HEALTH SCORE (0–100, ResearchIQ composite metric)
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_health_score(
        prep: Optional[PreprocessingResult],
        morph: Optional[MorphologyResult],
        stat: Optional[StatisticalAnalysisResult],
        sem: Optional[SemanticAnalysisResult],
        app: Optional[ApplicationAnalysisResult],
    ) -> Dict:
        scores = {}
        explanations = {}

        # 1. Readability (based on avg sentence length)
        avg_sent = prep.average_sentence_length if prep else 20
        if avg_sent <= 15:
            rb = 90
        elif avg_sent <= 20:
            rb = 75
        elif avg_sent <= 30:
            rb = 55
        else:
            rb = 35
        scores["readability"] = rb
        explanations["readability"] = (
            f"Avg sentence length is {avg_sent:.1f} words. "
            f"Shorter sentences (≤15 words) score highest. Source: Phase 3 Preprocessing."
        )

        # 2. Vocabulary Diversity (Type-Token Ratio)
        ttr = stat.type_token_ratio if stat else 0.0
        vd = min(100, round(ttr * 150))  # TTR of ~0.67+ → 100
        scores["vocabulary_diversity"] = vd
        explanations["vocabulary_diversity"] = (
            f"Type-Token Ratio is {ttr:.3f} (unique tokens / total tokens). "
            f"Higher TTR indicates richer vocabulary. Source: Phase 5 Statistical NLP."
        )

        # 3. Lexical Richness (vocabulary reduction from morphology)
        vr = morph.vocabulary_reduction_percentage if morph else 50.0
        # High reduction = lots of redundancy → lower richness
        lr = max(0, min(100, round(100 - vr)))
        scores["lexical_richness"] = lr
        explanations["lexical_richness"] = (
            f"Vocabulary reduction after lemmatization: {vr:.1f}%. "
            f"Lower reduction means richer, more varied word forms. Source: Phase 4 Morphology."
        )

        # 4. Entity Density
        ner_data = _safe_json(app.entities_json if app else None, {})
        entity_count = len(ner_data.get("entities", []))
        words = prep.token_count if prep else 1
        density = entity_count / max(1, words) * 100
        ed = min(100, round(density * 25))  # 4% density → score 100
        scores["entity_density"] = ed
        explanations["entity_density"] = (
            f"Found {entity_count} named entities in {words} tokens "
            f"({density:.2f}% density). Higher entity density indicates information richness. "
            f"Source: Phase 9A NER."
        )

        # 5. Semantic Coverage (words with WordNet senses)
        sem_pairs = _safe_json(sem.semantic_pairs_json if sem else None, [])
        sem_coverage = min(100, round(len(sem_pairs) / max(1, words) * 500))
        scores["semantic_coverage"] = sem_coverage
        explanations["semantic_coverage"] = (
            f"{len(sem_pairs)} words have WordNet semantic entries out of {words} tokens. "
            f"Higher coverage means better semantic grounding. Source: Phase 7 Semantic Analysis."
        )

        # 6. Structural Complexity (based on perplexity — moderate = good)
        perp = stat.perplexity_score if stat else 100.0
        # Ideal perplexity range ~50–200 for readable academic text
        if 50 <= perp <= 200:
            sc = 85
        elif perp < 50:
            sc = 60  # too simple
        elif perp <= 500:
            sc = 65
        else:
            sc = 40  # too complex
        scores["structural_complexity"] = sc
        explanations["structural_complexity"] = (
            f"Language model perplexity is {perp:.1f}. "
            f"Scores 50–200 reflect well-structured academic prose. "
            f"Source: Phase 5 Statistical NLP."
        )

        # 7. Summary Quality (compression ratio from summarization)
        sum_data = _safe_json(app.summary_json if app else None, {})
        comp_ratio = sum_data.get("statistics", {}).get("compression_ratio", 0.5)
        # Good extractive summary should compress to 20–40%
        if 0.2 <= comp_ratio <= 0.4:
            sq = 90
        elif comp_ratio < 0.2:
            sq = 60  # too few sentences selected
        else:
            sq = 70
        scores["summary_quality"] = sq
        explanations["summary_quality"] = (
            f"Extractive summarizer achieved {comp_ratio*100:.0f}% compression ratio. "
            f"Optimal range is 20–40%. Source: Phase 9A Summarization."
        )

        # ── Composite Score (weighted average) ─────────────────────────────────
        weights = {
            "readability": 0.20,
            "vocabulary_diversity": 0.15,
            "lexical_richness": 0.10,
            "entity_density": 0.15,
            "semantic_coverage": 0.15,
            "structural_complexity": 0.15,
            "summary_quality": 0.10,
        }
        composite = sum(scores[k] * weights[k] for k in weights)
        composite = round(composite)

        if composite >= 80:
            grade, badge = "Excellent", "success"
        elif composite >= 65:
            grade, badge = "Good", "info"
        elif composite >= 50:
            grade, badge = "Fair", "warning"
        else:
            grade, badge = "Needs Improvement", "danger"

        return {
            "composite": composite,
            "grade": grade,
            "badge": badge,
            "subscores": scores,
            "explanations": explanations,
            "weights": weights,
            "formula": "Weighted average of 7 subscores. Each subscore is computed from a specific Phase output.",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 3. READABILITY ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_readability(
        doc: Document,
        prep: Optional[PreprocessingResult],
        stat: Optional[StatisticalAnalysisResult],
    ) -> Dict:
        avg_sent = prep.average_sentence_length if prep else 0
        words = prep.token_count if prep else 1
        chars = doc.character_count or 0
        avg_word_len = round(chars / max(1, words), 2)
        vocab_size = stat.vocabulary_size if stat else 0
        ttr = stat.type_token_ratio if stat else 0

        # Flesch-Kincaid inspired heuristic (no syllable counter — use word length proxy)
        complexity_proxy = avg_word_len * avg_sent
        if complexity_proxy < 60:
            difficulty = "Easy"
            diff_badge = "success"
            diff_desc = "Suitable for general audiences. Clear and concise language."
        elif complexity_proxy < 120:
            difficulty = "Medium"
            diff_badge = "warning"
            diff_desc = "Requires moderate literacy. Academic or professional style."
        else:
            difficulty = "Hard"
            diff_badge = "danger"
            diff_desc = "Dense, technical content. Suitable for expert audiences."

        avg_wpm = 238
        reading_time = round(words / avg_wpm, 1)

        return {
            "avg_sentence_length": round(avg_sent, 2),
            "avg_word_length": avg_word_len,
            "vocabulary_size": vocab_size,
            "type_token_ratio": round(ttr, 4),
            "complexity_proxy": round(complexity_proxy, 2),
            "difficulty": difficulty,
            "difficulty_badge": diff_badge,
            "difficulty_description": diff_desc,
            "reading_time_min": reading_time,
            "explanation": (
                f"Difficulty is classified using Avg Sentence Length ({avg_sent:.1f} words) × "
                f"Avg Word Length ({avg_word_len:.2f} chars). "
                f"Score < 60 = Easy, 60–120 = Medium, > 120 = Hard. Source: Phase 3 + Phase 5."
            ),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 4. DOCUMENT COMPLEXITY
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_complexity(
        stat: Optional[StatisticalAnalysisResult],
        syn: Optional[Any],
        sem: Optional[SemanticAnalysisResult],
        morph: Optional[MorphologyResult],
        prep: Optional[PreprocessingResult],
    ) -> Dict:
        perplexity = stat.perplexity_score if stat else 0.0
        ambiguity = sem.ambiguity_score if sem else 0.0
        vocab_red = morph.vocabulary_reduction_percentage if morph else 0.0
        ttr = stat.type_token_ratio if stat else 0.0

        # POS distribution from syntax
        pos_dist = {}
        if syn and syn.pos_tags_json:
            pos_tags = _safe_json(syn.pos_tags_json, [])
            for tag in pos_tags:
                t = tag.get("tag", "X") if isinstance(tag, dict) else (tag[1] if len(tag) > 1 else "X")
                # Coarsen: NN* → NOUN, VB* → VERB, JJ* → ADJ etc.
                if t.startswith("NN"):
                    key = "NOUN"
                elif t.startswith("VB"):
                    key = "VERB"
                elif t.startswith("JJ"):
                    key = "ADJ"
                elif t.startswith("RB"):
                    key = "ADV"
                elif t in ("IN", "TO"):
                    key = "PREP"
                elif t in ("DT", "PDT"):
                    key = "DET"
                else:
                    key = "OTHER"
                pos_dist[key] = pos_dist.get(key, 0) + 1

        return {
            "perplexity": round(perplexity, 2),
            "ambiguity_score": round(ambiguity, 4),
            "lexical_diversity": round(ttr, 4),
            "vocabulary_reduction_pct": round(vocab_red, 2),
            "pos_distribution": pos_dist,
            "explanations": {
                "perplexity": "Language model perplexity. Lower = more predictable, higher = more complex. Source: Phase 5.",
                "ambiguity_score": "Proportion of words with multiple WordNet senses. Higher = more ambiguous. Source: Phase 7.",
                "lexical_diversity": "Type-Token Ratio (unique tokens / total). Higher = richer vocabulary. Source: Phase 5.",
                "vocabulary_reduction_pct": "% of unique word forms eliminated by lemmatization. Source: Phase 4.",
                "pos_distribution": "Distribution of grammatical roles across all tokens. Source: Phase 6.",
            },
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 5. RESEARCH INSIGHTS (Keywords, Topics, Concepts)
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_research_insights(
        stat: Optional[StatisticalAnalysisResult],
        app: Optional[ApplicationAnalysisResult],
        sem: Optional[SemanticAnalysisResult],
        morph: Optional[MorphologyResult],
    ) -> Dict:
        # Top keywords from application layer
        keywords = _safe_json(app.keywords_json if app else None, [])

        # Top TF-IDF from stats
        tfidf_raw = _safe_json(stat.tfidf_json if stat else None, {})
        if isinstance(tfidf_raw, dict):
            tfidf_sorted = sorted(tfidf_raw.items(), key=lambda x: x[1], reverse=True)[:20]
        else:
            tfidf_sorted = tfidf_raw[:20] if tfidf_raw else []

        # Topic clusters: group keywords into 6 pseudo-topics by TF-IDF score quartiles
        topics = []
        if keywords:
            chunk = max(1, len(keywords) // 6)
            for i in range(0, min(len(keywords), 6 * chunk), chunk):
                batch = keywords[i: i + chunk]
                if batch:
                    topic_words = [k["keyword"] for k in batch]
                    topics.append({
                        "name": f"Topic {len(topics)+1}: {topic_words[0].capitalize()}",
                        "keywords": topic_words,
                        "importance": round(batch[0].get("score", 0), 4),
                    })

        # Vocabulary stats
        vocab_size = stat.vocabulary_size if stat else 0
        total_tokens = stat.total_tokens if stat else 0
        unique_lemmas = morph.unique_lemmas if morph else 0
        ttr = stat.type_token_ratio if stat else 0

        # WordNet coverage
        sem_pairs = _safe_json(sem.semantic_pairs_json if sem else None, [])
        wordnet_coverage = len(sem_pairs)

        # Bigrams / frequent noun phrases from bigram_json
        bigrams_raw = _safe_json(stat.bigram_json if stat else None, [])
        top_bigrams = bigrams_raw[:10] if bigrams_raw else []

        return {
            "top_keywords": keywords[:20],
            "tfidf_top": tfidf_sorted[:15],
            "topics": topics[:6],
            "vocabulary_size": vocab_size,
            "total_tokens": total_tokens,
            "unique_lemmas": unique_lemmas,
            "type_token_ratio": round(ttr, 4),
            "wordnet_coverage": wordnet_coverage,
            "top_bigrams": top_bigrams,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 6. ENTITY INTELLIGENCE
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_entity_intelligence(app: Optional[ApplicationAnalysisResult]) -> Dict:
        if not app or not app.entities_json:
            return {"entities": [], "distribution": {}, "top_entities": [], "by_type": {}}

        ner_data = _safe_json(app.entities_json, {})
        entities = ner_data.get("entities", [])
        distribution = ner_data.get("distribution", {})
        top_entities = ner_data.get("top_entities", [])

        # Group by type
        by_type: Dict[str, List] = {}
        for e in entities:
            t = e.get("type", "MISC")
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(e["entity"])

        return {
            "entities": entities[:50],
            "distribution": distribution,
            "top_entities": top_entities[:20],
            "by_type": by_type,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 7. EXECUTIVE SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_executive_summary(
        app: Optional[ApplicationAnalysisResult],
        prag: Optional[PragmaticAnalysisResult],
        doc: Document,
    ) -> Dict:
        sum_data = _safe_json(app.summary_json if app else None, {})
        prag_summary = _safe_json(prag.pragmatic_summary_json if prag else None, {})
        intent_data = _safe_json(prag.intent_classification_json if prag else None, [])

        summary_text = sum_data.get("summary_text", "No summary available.")
        stats = sum_data.get("statistics", {})

        primary_intent = prag_summary.get("primary_intent", "Statement")
        avg_confidence = prag_summary.get("average_confidence", 0.0)

        # Derive communication style from intent
        intent_counts: Dict[str, int] = {}
        for item in (intent_data if isinstance(intent_data, list) else []):
            intent = item.get("intent", "Statement")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        dominant_intent = max(intent_counts, key=intent_counts.get) if intent_counts else "Statement"

        style_map = {
            "Question": "Interrogative / Investigative",
            "Statement": "Declarative / Informative",
            "Opinion": "Subjective / Analytical",
            "Suggestion": "Prescriptive / Advisory",
        }
        comm_style = style_map.get(dominant_intent, "Mixed")

        return {
            "summary_text": summary_text,
            "compression_ratio": stats.get("compression_ratio", 0),
            "original_sentences": stats.get("original_sentences", 0),
            "summary_sentences": stats.get("summary_sentences", 0),
            "primary_intent": primary_intent,
            "communication_style": comm_style,
            "avg_confidence": round(avg_confidence, 2),
            "source_phases": ["Phase 9A Summarization", "Phase 8 Pragmatics"],
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 8. PIPELINE TIMELINE
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_pipeline_timeline(
        doc: Document,
        prep: Optional[PreprocessingResult],
        morph: Optional[MorphologyResult],
        stat: Optional[StatisticalAnalysisResult],
        syn: Optional[Any],
        sem: Optional[SemanticAnalysisResult],
        prag: Optional[PragmaticAnalysisResult],
        app: Optional[ApplicationAnalysisResult],
        dash: Optional[ResearchDashboardResult],
    ) -> List[Dict]:
        def fmt(dt):
            return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

        stages = [
            {"phase": "Upload",           "icon": "bi-cloud-upload-fill",        "result": doc,   "color": "#6c757d"},
            {"phase": "Preprocessing",    "icon": "bi-scissors",                 "result": prep,  "color": "#0d6efd"},
            {"phase": "Morphology",       "icon": "bi-subtract",                 "result": morph, "color": "#6610f2"},
            {"phase": "Statistical NLP",  "icon": "bi-bar-chart-fill",           "result": stat,  "color": "#fd7e14"},
            {"phase": "Syntax Analysis",  "icon": "bi-diagram-3-fill",           "result": syn,   "color": "#198754"},
            {"phase": "Semantic Analysis","icon": "bi-bezier2",                  "result": sem,   "color": "#0dcaf0"},
            {"phase": "Pragmatics",       "icon": "bi-chat-quote-fill",          "result": prag,  "color": "#ffc107"},
            {"phase": "Applications",     "icon": "bi-app-indicator",            "result": app,   "color": "#dc3545"},
            {"phase": "Research Intel.",  "icon": "bi-trophy-fill",              "result": dash,  "color": "#20c997"},
        ]

        timeline = []
        for s in stages:
            r = s["result"]
            ts = None
            if r is not None:
                ts = fmt(getattr(r, "processed_at", None) or getattr(r, "upload_date", None))
            timeline.append({
                "phase": s["phase"],
                "icon": s["icon"],
                "color": s["color"],
                "completed": r is not None,
                "timestamp": ts,
                "output": "Stored in DB" if r is not None else "Not yet run",
            })
        return timeline

    # ─────────────────────────────────────────────────────────────────────────
    # 9. BUILD & PERSIST FULL DASHBOARD
    # ─────────────────────────────────────────────────────────────────────────
    @classmethod
    def build(cls, document_id: int) -> Optional["ResearchDashboardResult"]:
        """Aggregates all phase outputs and stores dashboard data."""
        doc = db.session.get(Document, document_id)
        if not doc:
            logger.error(f"Document {document_id} not found.")
            return None

        # Load all phase results
        prep = PreprocessingResult.query.filter_by(document_id=document_id).first()
        morph = MorphologyResult.query.filter_by(document_id=document_id).first()
        stat = StatisticalAnalysisResult.query.filter_by(document_id=document_id).first()
        syn = SyntaxAnalysisResult.query.filter_by(document_id=document_id).first()
        sem = SemanticAnalysisResult.query.filter_by(document_id=document_id).first()
        prag = PragmaticAnalysisResult.query.filter_by(document_id=document_id).first()
        app = ApplicationAnalysisResult.query.filter_by(document_id=document_id).first()

        try:
            overview    = cls.compute_document_overview(doc, prep)
            health      = cls.compute_health_score(prep, morph, stat, sem, app)
            readability = cls.compute_readability(doc, prep, stat)
            complexity  = cls.compute_complexity(stat, syn, sem, morph, prep)
            insights    = cls.compute_research_insights(stat, app, sem, morph)
            entities    = cls.compute_entity_intelligence(app)
            ex_summary  = cls.compute_executive_summary(app, prag, doc)
            timeline    = cls.compute_pipeline_timeline(doc, prep, morph, stat, syn, sem, prag, app, None)

            dash = ResearchDashboardResult.query.filter_by(document_id=document_id).first()
            if not dash:
                dash = ResearchDashboardResult(document_id=document_id)
                db.session.add(dash)

            dash.document_overview_json   = json.dumps(overview)
            dash.health_score_json        = json.dumps(health)
            dash.readability_json         = json.dumps(readability)
            dash.complexity_json          = json.dumps(complexity)
            dash.research_insights_json   = json.dumps(insights)
            dash.entity_intelligence_json = json.dumps(entities)
            dash.executive_summary_json   = json.dumps(ex_summary)
            dash.pipeline_timeline_json   = json.dumps(timeline)
            dash.processed_at             = datetime.now(timezone.utc)

            db.session.commit()
            logger.info(f"Dashboard built for document {document_id}")
            return dash

        except Exception as e:
            db.session.rollback()
            logger.exception(f"Failed to build dashboard for document {document_id}: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # 10. COMPARE TWO DOCUMENTS
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compare_documents(doc_id_1: int, doc_id_2: int) -> Dict:
        """Returns a side-by-side comparison of two documents' dashboard metrics."""
        def load(doc_id):
            dash = ResearchDashboardResult.query.filter_by(document_id=doc_id).first()
            doc = db.session.get(Document, doc_id)
            if not dash or not doc:
                return None
            return {
                "doc_id": doc_id,
                "filename": doc.original_filename,
                "overview": _safe_json(dash.document_overview_json),
                "health": _safe_json(dash.health_score_json),
                "readability": _safe_json(dash.readability_json),
                "insights": _safe_json(dash.research_insights_json),
                "complexity": _safe_json(dash.complexity_json),
            }

        d1 = load(doc_id_1)
        d2 = load(doc_id_2)

        if not d1 or not d2:
            return {"error": "One or both documents have no dashboard data. Run pipeline first."}

        # Compute deltas for numeric fields
        def delta(k1, k2, key):
            v1 = k1.get(key, 0) or 0
            v2 = k2.get(key, 0) or 0
            return round(v2 - v1, 2)

        return {
            "doc1": d1,
            "doc2": d2,
            "deltas": {
                "health_score": delta(d1["health"], d2["health"], "composite"),
                "words": delta(d1["overview"], d2["overview"], "words"),
                "reading_time": delta(d1["overview"], d2["overview"], "reading_time_min"),
                "avg_sentence_length": delta(d1["readability"], d2["readability"], "avg_sentence_length"),
                "vocabulary_size": delta(d1["insights"], d2["insights"], "vocabulary_size"),
                "perplexity": delta(d1["complexity"], d2["complexity"], "perplexity"),
            },
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 11. BATCH ANALYSIS SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def batch_summary(user_id: int) -> List[Dict]:
        """Returns a summary row for every document belonging to the user."""
        from models.document import Document as Doc
        docs = Doc.query.filter_by(user_id=user_id).all()
        rows = []
        for doc in docs:
            dash = ResearchDashboardResult.query.filter_by(document_id=doc.id).first()
            health = _safe_json(dash.health_score_json if dash else None, {})
            overview = _safe_json(dash.document_overview_json if dash else None, {})
            readability = _safe_json(dash.readability_json if dash else None, {})
            rows.append({
                "doc_id": doc.id,
                "filename": doc.original_filename,
                "status": doc.status,
                "words": overview.get("words", doc.word_count or 0),
                "reading_time_min": overview.get("reading_time_min", 0),
                "health_score": health.get("composite", "N/A"),
                "health_grade": health.get("grade", "N/A"),
                "difficulty": readability.get("difficulty", "N/A"),
                "has_dashboard": dash is not None,
            })
        return rows
