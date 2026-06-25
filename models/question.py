"""
Question Model
Stores Q&A pairs linked to uploaded documents.
"""

from datetime import datetime, timezone
from app_extensions import db


class Question(db.Model):
    """User question and system-generated answer for a document."""

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, default="")
    confidence = db.Column(db.Float, default=0.0)   # 0.0–1.0 confidence score (future use)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Question doc={self.document_id} q={self.question[:40]}>"
