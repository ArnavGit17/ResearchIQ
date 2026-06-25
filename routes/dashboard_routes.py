"""
routes/dashboard_routes.py
Dashboard blueprint – overview statistics and home page.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


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
    # Fetch 5 most recent documents for the dashboard preview
    from services.upload_service import UploadService
    recent_docs = UploadService.get_user_documents(current_user.id)[:5]
    return render_template("dashboard/index.html", stats=stats, recent_docs=recent_docs)
