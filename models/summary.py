"""
Summary Model
Stores AI-generated document summaries.
"""

from datetime import datetime, timezone
from app_extensions import db


class Summary(db.Model):
    """Generated summary for a document."""

    __tablename__ = "summaries"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False, index=True)
    summary = db.Column(db.Text, nullable=False)
    summary_type = db.Column(db.String(20), default="abstractive")  # abstractive | extractive
    word_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Summary doc={self.document_id} words={self.word_count}>"
