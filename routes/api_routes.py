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
