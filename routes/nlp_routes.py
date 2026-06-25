"""
routes/nlp_routes.py
NLP Laboratory blueprint – placeholder pages for all analysis modules.
"""

import json
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app_extensions import db
from models.document import Document
from models.preprocessing import PreprocessingResult

nlp_bp = Blueprint("nlp", __name__, url_prefix="/nlp")


@nlp_bp.route("/laboratory")
@login_required
def laboratory():
    doc_id = request.args.get('doc', type=int)
    document = None
    prep_result = None
    
    if doc_id:
        document = db.session.get(Document, doc_id)
        if not document or document.user_id != current_user.id:
            flash("Document not found or access denied.", "danger")
            return redirect(url_for('document_bp.index'))
            
        prep_result = PreprocessingResult.query.filter_by(document_id=document.id).first()
        
    return render_template("nlp/laboratory.html", 
                           page="laboratory", 
                           document=document, 
                           prep_result=prep_result)


@nlp_bp.route("/syntax")
@login_required
def syntax():
    return render_template("nlp/placeholder.html",
                           page="syntax",
                           title="Syntax Analysis",
                           icon="bi-diagram-3",
                           description="Dependency parsing, constituency trees, and grammatical relation extraction.",
                           status="Coming in Phase 2")


@nlp_bp.route("/semantic")
@login_required
def semantic():
    return render_template("nlp/placeholder.html",
                           page="semantic",
                           title="Semantic Analysis",
                           icon="bi-bezier2",
                           description="Named entity recognition, word sense disambiguation, and semantic role labelling.",
                           status="Coming in Phase 2")


@nlp_bp.route("/pragmatic")
@login_required
def pragmatic():
    return render_template("nlp/placeholder.html",
                           page="pragmatic",
                           title="Pragmatic Analysis",
                           icon="bi-chat-quote",
                           description="Sentiment analysis, discourse analysis, and speech act detection.",
                           status="Coming in Phase 2")


@nlp_bp.route("/assistant")
@login_required
def assistant():
    return render_template("nlp/placeholder.html",
                           page="assistant",
                           title="Research Assistant",
                           icon="bi-robot",
                           description="AI-powered research guidance and literature gap identification.",
                           status="Coming in Phase 3")


@nlp_bp.route("/search")
@login_required
def search():
    return render_template("nlp/placeholder.html",
                           page="search",
                           title="Semantic Search",
                           icon="bi-search-heart",
                           description="Dense vector search across your uploaded research corpus.",
                           status="Coming in Phase 3")


@nlp_bp.route("/qa")
@login_required
def qa():
    return render_template("nlp/placeholder.html",
                           page="qa",
                           title="Question Answering",
                           icon="bi-patch-question",
                           description="Ask natural-language questions and get evidence-backed answers.",
                           status="Coming in Phase 3")


@nlp_bp.route("/summarization")
@login_required
def summarization():
    return render_template("nlp/placeholder.html",
                           page="summarization",
                           title="Summarization",
                           icon="bi-file-earmark-check",
                           description="Extractive and abstractive summarisation of research documents.",
                           status="Coming in Phase 3")
