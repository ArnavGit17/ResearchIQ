"""
routes/analytics_routes.py
Analytics blueprint – usage statistics visualisation.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.document import Document
from models.analysis import Analysis
from app_extensions import db

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/")
@login_required
def index():
    """Analytics overview page."""
    # Document type distribution
    from sqlalchemy import func
    type_counts = (
        db.session.query(Document.file_type, func.count(Document.id))
        .filter_by(user_id=current_user.id)
        .group_by(Document.file_type)
        .all()
    )
    type_labels = [r[0].upper() for r in type_counts]
    type_values = [r[1] for r in type_counts]

    # Text Statistics (Phase 2)
    total_words = db.session.query(func.sum(Document.word_count)).filter_by(user_id=current_user.id).scalar() or 0
    total_sentences = db.session.query(func.sum(Document.sentence_count)).filter_by(user_id=current_user.id).scalar() or 0
    
    avg_length = 0
    if current_user.document_count > 0:
        avg_length = int(total_words / current_user.document_count)


    stats = {
        "documents": current_user.document_count,
        "analyses":  current_user.analysis_count,
        "questions": current_user.question_count,
        "summaries": current_user.summary_count,
        "total_words": total_words,
        "total_sentences": total_sentences,
        "avg_length": avg_length
    }
    return render_template(
        "analytics/index.html",
        stats=stats,
        type_labels=type_labels,
        type_values=type_values,
    )
