"""
routes/dashboard_routes.py
Dashboard blueprint – overview statistics, home page, and Research Intelligence Dashboard.
"""

import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from app_extensions import db
from models.document import Document
from models.research_dashboard import ResearchDashboardResult
from services.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def _safe_json(val, default=None):
    if not val:
        return default if default is not None else {}
    try:
        return json.loads(val)
    except Exception:
        return default if default is not None else {}


@dashboard_bp.route("/")
@login_required
def index():
    """Main dashboard with statistics cards."""
    stats = {
        "documents": current_user.document_count,
        "analyses":  current_user.analysis_count,
        "questions": current_user.question_count,
        "summaries": current_user.summary_count,
    }
    from services.upload_service import UploadService
    recent_docs = UploadService.get_user_documents(current_user.id)[:5]
    return render_template("dashboard/index.html", stats=stats, recent_docs=recent_docs)


@dashboard_bp.route("/research/<int:document_id>")
@login_required
def research_intelligence(document_id: int):
    """Research Intelligence Dashboard for a specific document."""
    doc = db.session.get(Document, document_id)
    if not doc or doc.user_id != current_user.id:
        return render_template("errors/404.html"), 404

    # Build (or refresh) the dashboard data
    dash = DashboardService.build(document_id)

    # Load all JSON sections
    def sj(field):
        return _safe_json(getattr(dash, field, None), {}) if dash else {}

    overview      = sj("document_overview_json")
    health        = sj("health_score_json")
    readability   = sj("readability_json")
    complexity    = sj("complexity_json")
    insights      = sj("research_insights_json")
    entities      = sj("entity_intelligence_json")
    ex_summary    = sj("executive_summary_json")
    pipeline      = _safe_json(dash.pipeline_timeline_json, []) if dash else []

    # User docs for document selector
    from services.upload_service import UploadService
    user_docs = UploadService.get_user_documents(current_user.id)

    return render_template(
        "dashboard/research_intelligence.html",
        document=doc,
        overview=overview,
        health=health,
        readability=readability,
        complexity=complexity,
        insights=insights,
        entities=entities,
        ex_summary=ex_summary,
        pipeline=pipeline,
        user_docs=user_docs,
        page="research_intelligence",
    )


@dashboard_bp.route("/compare")
@login_required
def compare():
    """Document Comparison Dashboard."""
    from services.upload_service import UploadService
    user_docs = UploadService.get_user_documents(current_user.id)

    doc1_id = request.args.get("doc1", type=int)
    doc2_id = request.args.get("doc2", type=int)

    comparison = None
    if doc1_id and doc2_id:
        comparison = DashboardService.compare_documents(doc1_id, doc2_id)

    return render_template(
        "dashboard/compare.html",
        user_docs=user_docs,
        comparison=comparison,
        doc1_id=doc1_id,
        doc2_id=doc2_id,
        page="compare",
    )


@dashboard_bp.route("/batch")
@login_required
def batch():
    """Batch Analysis Dashboard — overview of all user documents."""
    rows = DashboardService.batch_summary(current_user.id)
    return render_template(
        "dashboard/batch.html",
        rows=rows,
        page="batch",
    )
