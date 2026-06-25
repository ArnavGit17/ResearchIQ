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
from services.nlp_pipeline import NLPPipeline

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
