"""
API Routes
Provides endpoints for asynchronous NLP processing and data retrieval.
"""

import json
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app_extensions import db
from models.document import Document
from models.preprocessing import PreprocessingResult
from models.morphology import MorphologyResult
from models.statistical_nlp import StatisticalAnalysisResult
from models.syntax import SyntaxAnalysisResult
from models.semantic import SemanticAnalysisResult
from models.application import ApplicationAnalysisResult
from services.nlp_pipeline import NLPPipeline
from services.question_answering_service import QAService
from services.search_service import SemanticSearchService

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/preprocess/<int:document_id>", methods=["POST"])
@login_required
def run_preprocess(document_id: int):
    """Run NLP preprocessing on a document."""
    # Ensure document exists and belongs to user
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404
        
    if not document.cleaned_text:
        return jsonify({"error": "Document contains no extractable text"}), 400
        
    success = NLPPipeline.run_preprocessing(document_id)
    
    if success:
        return jsonify({"status": "success", "message": "Document processed successfully"}), 200
    else:
        return jsonify({"error": "Failed to process document"}), 500


@api_bp.route("/preprocess/<int:document_id>", methods=["GET"])
@login_required
def get_preprocess_results(document_id: int):
    """Get preprocessing results for a document."""
    # Ensure document exists and belongs to user
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404
        
    prep_result = PreprocessingResult.query.filter_by(document_id=document_id).first()
    
    if not prep_result:
        return jsonify({"error": "Document has not been processed yet"}), 404
        
    # Safely parse JSON or return empty lists if corrupt
    try:
        tokens = json.loads(prep_result.tokens_json) if prep_result.tokens_json else []
    except Exception:
        tokens = []
        
    try:
        sentences = json.loads(prep_result.sentences_json) if prep_result.sentences_json else []
    except Exception:
        sentences = []
        
    return jsonify({
        "document_id": prep_result.document_id,
        "token_count": prep_result.token_count,
        "sentence_count": prep_result.sentence_count,
        "unique_token_count": prep_result.unique_token_count,
        "vocabulary_size": prep_result.vocabulary_size,
        "average_sentence_length": prep_result.average_sentence_length,
        "normalized_text": prep_result.normalized_text,
        "tokens": tokens,
        "sentences": sentences,
        "processed_at": prep_result.processed_at.isoformat() if prep_result.processed_at else None
    })

@api_bp.route("/morphology/<int:document_id>", methods=["POST"])
@login_required
def run_morphology(document_id: int):
    """Run NLP morphology on a document."""
    # Ensure document exists and belongs to user
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404
        
    success = NLPPipeline.run_morphology(document_id)
    
    if success:
        return jsonify({"status": "success", "message": "Morphology processed successfully"}), 200
    else:
        return jsonify({"error": "Failed to process morphology. Please ensure preprocessing is complete."}), 500


@api_bp.route("/morphology/<int:document_id>", methods=["GET"])
@login_required
def get_morphology_results(document_id: int):
    """Get morphology results for a document."""
    # Ensure document exists and belongs to user
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404
        
    morph_result = MorphologyResult.query.filter_by(document_id=document_id).first()
    
    if not morph_result:
        return jsonify({"error": "Morphology has not been processed yet"}), 404
        
    try:
        stems = json.loads(morph_result.stemmed_tokens_json) if morph_result.stemmed_tokens_json else []
        lemmas = json.loads(morph_result.lemmatized_tokens_json) if morph_result.lemmatized_tokens_json else []
        pairs = json.loads(morph_result.morphology_pairs_json) if morph_result.morphology_pairs_json else []
    except Exception:
        stems, lemmas, pairs = [], [], []
        
    return jsonify({
        "document_id": morph_result.document_id,
        "unique_stems": morph_result.unique_stems,
        "unique_lemmas": morph_result.unique_lemmas,
        "stem_count": morph_result.stem_count,
        "lemma_count": morph_result.lemma_count,
        "original_vocabulary_size": morph_result.original_vocabulary_size,
        "stemmed_vocabulary_size": morph_result.stemmed_vocabulary_size,
        "lemmatized_vocabulary_size": morph_result.lemmatized_vocabulary_size,
        "vocabulary_reduction_percentage": morph_result.vocabulary_reduction_percentage,
        "stems": stems,
        "lemmas": lemmas,
        "morphology_pairs": pairs,
        "processed_at": morph_result.processed_at.isoformat() if morph_result.processed_at else None
    })


@api_bp.route("/statistical/<int:document_id>", methods=["POST"])
@login_required
def run_statistical(document_id: int):
    """Run Statistical NLP analysis (Phase 5) on a document."""
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    success = NLPPipeline.run_statistical_analysis(document_id)

    if success:
        return jsonify({"status": "success", "message": "Statistical analysis completed"}), 200
    else:
        return jsonify({"error": "Failed. Ensure morphological analysis is complete first."}), 500


@api_bp.route("/statistical/<int:document_id>", methods=["GET"])
@login_required
def get_statistical(document_id: int):
    """Return Statistical NLP results as JSON."""
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    stat = StatisticalAnalysisResult.query.filter_by(document_id=document_id).first()
    if not stat:
        return jsonify({"error": "Statistical analysis has not been run yet"}), 404

    def _safe_load(field):
        try:
            return json.loads(field) if field else []
        except Exception:
            return []

    return jsonify({
        "document_id":        stat.document_id,
        "vocabulary_size":    stat.vocabulary_size,
        "total_tokens":       stat.total_tokens,
        "unique_bigrams":     stat.unique_bigrams,
        "unique_trigrams":    stat.unique_trigrams,
        "type_token_ratio":   stat.type_token_ratio,
        "perplexity_score":   stat.perplexity_score,
        "unigrams":           _safe_load(stat.unigram_json),
        "bigrams":            _safe_load(stat.bigram_json),
        "trigrams":           _safe_load(stat.trigram_json),
        "tf":                 _safe_load(stat.tf_json),
        "tfidf":              _safe_load(stat.tfidf_json),
        "language_model":     _safe_load(stat.language_model_json),
        "perplexity_detail":  _safe_load(stat.perplexity_detail_json),
        "processed_at":       stat.processed_at.isoformat() if stat.processed_at else None,
    })


@api_bp.route("/syntax/<int:document_id>", methods=["POST"])
@login_required
def run_syntax(document_id: int):
    """Run Syntax Analysis (Phase 6) on a document."""
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    success = NLPPipeline.run_syntax_analysis(document_id)

    if success:
        return jsonify({"status": "success", "message": "Syntax analysis completed"}), 200
    else:
        return jsonify({"error": "Failed. Ensure previous phases are complete."}), 500


@api_bp.route("/syntax/<int:document_id>", methods=["GET"])
@login_required
def get_syntax(document_id: int):
    """Return Syntax NLP results as JSON."""
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    syn = SyntaxAnalysisResult.query.filter_by(document_id=document_id).first()
    if not syn:
        return jsonify({"error": "Syntax analysis has not been run yet"}), 404

    def _safe_load(field):
        try:
            return json.loads(field) if field else []
        except Exception:
            return []

    return jsonify({
        "document_id":               syn.document_id,
        "noun_count":                syn.noun_count,
        "verb_count":                syn.verb_count,
        "adjective_count":           syn.adjective_count,
        "adverb_count":              syn.adverb_count,
        "other_count":               syn.other_count,
        "total_tagged_tokens":       syn.total_tagged_tokens,
        "noun_verb_ratio":           syn.noun_verb_ratio,
        "avg_pos_per_sentence":      syn.avg_pos_per_sentence,
        "sentence_complexity_score": syn.sentence_complexity_score,
        "dependency_engine":         syn.dependency_engine,
        "pos_tags":                  _safe_load(syn.pos_tags_json),
        "syntax_pairs":              _safe_load(syn.syntax_pairs_json),
        "tag_frequency":             _safe_load(syn.tag_frequency_json),
        "parse_tree":                _safe_load(syn.parse_tree_json),
        "parse_tree_text":           _safe_load(syn.parse_tree_text),
        "dependency":                _safe_load(syn.dependency_json),
        "processed_at":              syn.processed_at.isoformat() if syn.processed_at else None,
    })


@api_bp.route("/semantic/<int:document_id>", methods=["POST"])
@login_required
def run_semantic(document_id: int):
    """Run Semantic Analysis (Phase 7) on a document."""
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    success = NLPPipeline.run_semantic_analysis(document_id)

    if success:
        return jsonify({"status": "success", "message": "Semantic analysis completed"}), 200
    else:
        return jsonify({"error": "Failed. Ensure previous phases are complete."}), 500


@api_bp.route("/semantic/<int:document_id>", methods=["GET"])
@login_required
def get_semantic(document_id: int):
    """Return Semantic NLP results as JSON (Phase 7)."""
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    sem = SemanticAnalysisResult.query.filter_by(document_id=document_id).first()
    if not sem:
        return jsonify({"error": "Semantic analysis has not been run yet"}), 404

    def _safe_load(field, default=None):
        try:
            return json.loads(field) if field else (default if default is not None else [])
        except Exception:
            return default if default is not None else []

    ws_packed = _safe_load(sem.word_senses_json, {})

    return jsonify({
        "document_id":          sem.document_id,
        "ambiguity_score":      sem.ambiguity_score,
        "synonyms":             _safe_load(sem.synonyms_json, {}),
        "antonyms":             _safe_load(sem.antonyms_json, {}),
        "hypernyms":            _safe_load(sem.hypernyms_json, {}),
        "hyponyms":             _safe_load(sem.hyponyms_json, {}),
        "semantic_pairs":       _safe_load(sem.semantic_pairs_json, []),
        "semantic_similarity":  _safe_load(sem.semantic_similarity_json, []),
        "word_senses":          ws_packed.get("wsd",      []) if isinstance(ws_packed, dict) else [],
        "ambiguous_words":      ws_packed.get("ambiguous", []) if isinstance(ws_packed, dict) else [],
        "wordnet_coverage":     ws_packed.get("coverage",  {}) if isinstance(ws_packed, dict) else {},
        "processed_at":         sem.processed_at.isoformat() if sem.processed_at else None,
    })


@api_bp.route("/pragmatic/<int:document_id>", methods=["POST"])
@login_required
def run_pragmatic(document_id: int):
    """Run Pragmatic Analysis (Phase 8) on a document."""
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    success = NLPPipeline.run_pragmatic_analysis(document_id)

    if success:
        return jsonify({"status": "success", "message": "Pragmatic analysis completed"}), 200
    else:
        return jsonify({"error": "Failed. Ensure previous phases are complete."}), 500


@api_bp.route("/applications/<int:document_id>", methods=["POST"])
@login_required
def run_applications(document_id: int):
    """Run Applications Analysis (Phase 9A) on a document."""
    document = db.session.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    success = NLPPipeline.run_application_analysis(document_id)

    if success:
        return jsonify({"status": "success", "message": "Applications analysis completed"}), 200
    else:
        return jsonify({"error": "Failed. Ensure previous phases are complete."}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Phase 9B: Research Intelligence Dashboard API
# ─────────────────────────────────────────────────────────────────────────────

from models.research_dashboard import ResearchDashboardResult
from services.dashboard_service import DashboardService


@api_bp.route("/research-dashboard/<int:document_id>", methods=["GET"])
@login_required
def api_research_dashboard(document_id: int):
    """GET: Return complete aggregated Research Intelligence data for a document."""
    doc = db.session.get(Document, document_id)
    if not doc or doc.user_id != current_user.id:
        return jsonify({"error": "Document not found"}), 404

    dash = DashboardService.build(document_id)
    if not dash:
        return jsonify({"error": "Failed to build dashboard — ensure earlier pipeline phases have run."}), 500

    def sj(field):
        val = getattr(dash, field, None)
        if not val:
            return {}
        try:
            return json.loads(val)
        except Exception:
            return {}

    return jsonify({
        "document_id": document_id,
        "overview": sj("document_overview_json"),
        "health_score": sj("health_score_json"),
        "readability": sj("readability_json"),
        "complexity": sj("complexity_json"),
        "research_insights": sj("research_insights_json"),
        "entity_intelligence": sj("entity_intelligence_json"),
        "executive_summary": sj("executive_summary_json"),
        "pipeline_timeline": json.loads(dash.pipeline_timeline_json) if dash.pipeline_timeline_json else [],
        "processed_at": dash.processed_at.isoformat() if dash.processed_at else None,
    }), 200


@api_bp.route("/document-comparison", methods=["GET"])
@login_required
def api_document_comparison():
    """GET: Compare two documents side-by-side. Query params: doc1=<id>&doc2=<id>"""
    doc1_id = request.args.get("doc1", type=int)
    doc2_id = request.args.get("doc2", type=int)

    if not doc1_id or not doc2_id:
        return jsonify({"error": "Provide both doc1 and doc2 query parameters."}), 400

    # Security: ensure both docs belong to current user
    for did in [doc1_id, doc2_id]:
        doc = db.session.get(Document, did)
        if not doc or doc.user_id != current_user.id:
            return jsonify({"error": f"Document {did} not found."}), 404

    result = DashboardService.compare_documents(doc1_id, doc2_id)
    return jsonify(result), 200


@api_bp.route("/export-report/<int:document_id>", methods=["POST"])
@login_required
def api_export_report(document_id: int):
    """POST: Return full JSON export of all dashboard data for a document."""
    doc = db.session.get(Document, document_id)
    if not doc or doc.user_id != current_user.id:
        return jsonify({"error": "Document not found"}), 404

    dash = ResearchDashboardResult.query.filter_by(document_id=document_id).first()
    if not dash:
        # Try to build it
        dash = DashboardService.build(document_id)
    if not dash:
        return jsonify({"error": "No dashboard data available."}), 404

    def sj(field):
        val = getattr(dash, field, None)
        try:
            return json.loads(val) if val else {}
        except Exception:
            return {}

    export_data = {
        "meta": {
            "document": doc.original_filename,
            "exported_at": dash.processed_at.isoformat() if dash.processed_at else None,
            "platform": "ResearchIQ",
        },
        "overview": sj("document_overview_json"),
        "executive_summary": sj("executive_summary_json"),
        "health_score": sj("health_score_json"),
        "readability": sj("readability_json"),
        "complexity": sj("complexity_json"),
        "research_insights": sj("research_insights_json"),
        "entity_intelligence": sj("entity_intelligence_json"),
        "pipeline_timeline": json.loads(dash.pipeline_timeline_json) if dash.pipeline_timeline_json else [],
    }

    return jsonify(export_data), 200


@api_bp.route("/batch-summary", methods=["GET"])
@login_required
def api_batch_summary():
    """GET: Return batch summary for all user documents."""
    rows = DashboardService.batch_summary(current_user.id)
    return jsonify({"documents": rows, "total": len(rows)}), 200
