"""
Analysis Model
Records NLP analysis runs performed on documents.
"""

from datetime import datetime, timezone
from app_extensions import db


class Analysis(db.Model):
    """NLP analysis result linked to a document."""

    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False, index=True)

    # e.g. morphology | syntax | semantic | pragmatic | preprocessing
    analysis_type = db.Column(db.String(50), nullable=False)

    result_json = db.Column(db.Text, default="")      # JSON-serialised results (future use)
    status = db.Column(db.String(20), default="pending")  # pending | completed | failed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Analysis {self.analysis_type} doc={self.document_id}>"
