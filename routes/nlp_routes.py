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
from models.morphology import MorphologyResult
from models.statistical_nlp import StatisticalAnalysisResult
from models.syntax import SyntaxAnalysisResult
from models.semantic import SemanticAnalysisResult
from models.pragmatic import PragmaticAnalysisResult
from services.syntax_service import HMMViterbiDemoService

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


@nlp_bp.route("/morphology")
@login_required
def morphology():
    doc_id = request.args.get('doc', type=int)
    document = None
    morph_result = None
    prep_result = None
    
    if doc_id:
        document = db.session.get(Document, doc_id)
        if not document or document.user_id != current_user.id:
            flash("Document not found or access denied.", "danger")
            return redirect(url_for('document_bp.index'))
            
        morph_result = MorphologyResult.query.filter_by(document_id=document.id).first()
        prep_result = PreprocessingResult.query.filter_by(document_id=document.id).first()
        
    return render_template("nlp/morphology.html", 
                           page="morphology", 
                           document=document, 
                           morph_result=morph_result,
                           prep_result=prep_result)


@nlp_bp.route("/statistical-nlp")
@login_required
def statistical_nlp():
    doc_id = request.args.get('doc', type=int)
    document = None
    stat_result = None
    morph_result = None

    if doc_id:
        document = db.session.get(Document, doc_id)
        if not document or document.user_id != current_user.id:
            flash("Document not found or access denied.", "danger")
            return redirect(url_for('document_bp.index'))

        stat_result  = StatisticalAnalysisResult.query.filter_by(document_id=document.id).first()
        morph_result = MorphologyResult.query.filter_by(document_id=document.id).first()

    return render_template(
        "nlp/statistical.html",
        page="statistical",
        document=document,
        stat_result=stat_result,
        morph_result=morph_result,
    )


@nlp_bp.route("/syntax")
@login_required
def syntax():
    doc_id = request.args.get('doc', type=int)
    document = None
    syn_result = None
    stat_result = None

    if doc_id:
        document = db.session.get(Document, doc_id)
        if not document or document.user_id != current_user.id:
            flash("Document not found or access denied.", "danger")
            return redirect(url_for('document_bp.index'))

        syn_result  = SyntaxAnalysisResult.query.filter_by(document_id=document.id).first()
        stat_result = StatisticalAnalysisResult.query.filter_by(document_id=document.id).first()

    hmm_demo = HMMViterbiDemoService.get_hmm_demo()
    viterbi_demo = HMMViterbiDemoService.get_viterbi_demo()

    return render_template(
        "nlp/syntax.html",
        page="syntax",
        document=document,
        syn_result=syn_result,
        stat_result=stat_result,
        hmm_demo=hmm_demo,
        viterbi_demo=viterbi_demo,
    )


@nlp_bp.route("/semantic")
@login_required
def semantic():
    doc_id = request.args.get('doc', type=int)
    document = None
    sem_result = None
    syn_result = None

    if doc_id:
        document = db.session.get(Document, doc_id)
        if not document or document.user_id != current_user.id:
            flash("Document not found or access denied.", "danger")
            return redirect(url_for('document_bp.index'))

        sem_result = SemanticAnalysisResult.query.filter_by(document_id=document.id).first()
        syn_result = SyntaxAnalysisResult.query.filter_by(document_id=document.id).first()

    return render_template(
        "nlp/semantic.html",
        page="semantic",
        document=document,
        sem_result=sem_result,
        syn_result=syn_result,
    )


@nlp_bp.route("/pragmatic")
@login_required
def pragmatic():
    doc_id = request.args.get("doc")
    document = None
    prag_result = None

    if doc_id:
        document = db.session.get(Document, doc_id)
        if document and document.user_id == current_user.id:
            prag_result = PragmaticAnalysisResult.query.filter_by(document_id=doc_id).first()

    return render_template(
        "nlp/pragmatic.html",
        page="pragmatic",
        document=document,
        prag_result=prag_result
    )


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
