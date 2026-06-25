"""
Preprocessing Model
Tracks the NLP preprocessing outputs for documents.
"""

from datetime import datetime, timezone
from app_extensions import db


class PreprocessingResult(db.Model):
    """Stores tokenization, normalization, and stats for a document."""

    __tablename__ = "preprocessing_results"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Statistics
    token_count = db.Column(db.Integer, default=0)
    sentence_count = db.Column(db.Integer, default=0)
    unique_token_count = db.Column(db.Integer, default=0)
    vocabulary_size = db.Column(db.Integer, default=0)
    average_sentence_length = db.Column(db.Float, default=0.0)
    
    # Content
    normalized_text = db.Column(db.Text, nullable=True)
    tokens_json = db.Column(db.Text, nullable=True)      # Stored as JSON string
    sentences_json = db.Column(db.Text, nullable=True)   # Stored as JSON string
    
    # Meta
    processed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship back to Document
    document_ref = db.relationship("Document", backref=db.backref("preprocessing_result", uselist=False, lazy="joined", cascade="all, delete-orphan"))

    def __repr__(self) -> str:
        return f"<PreprocessingResult for Document {self.document_id}>"
