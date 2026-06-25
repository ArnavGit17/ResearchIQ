"""
Document Model
Tracks uploaded research documents.
"""

from datetime import datetime, timezone
from app_extensions import db


class Document(db.Model):
    """Uploaded document record."""

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)   # pdf | docx | txt
    file_size = db.Column(db.Integer, default=0)           # bytes
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default="uploaded")  # uploaded | processing | ready | error

    # Document Content & Statistics (Phase 2)
    raw_text = db.Column(db.Text, nullable=True)
    cleaned_text = db.Column(db.Text, nullable=True)
    word_count = db.Column(db.Integer, default=0)
    sentence_count = db.Column(db.Integer, default=0)
    character_count = db.Column(db.Integer, default=0)
    processing_status = db.Column(db.String(20), default="pending") # pending | success | failed
    processed_at = db.Column(db.DateTime, nullable=True)


    # Relationships
    analyses = db.relationship("Analysis", backref="document", lazy="dynamic", cascade="all, delete-orphan")
    questions = db.relationship("Question", backref="document", lazy="dynamic", cascade="all, delete-orphan")
    summaries = db.relationship("Summary", backref="document", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def file_size_display(self) -> str:
        """Human-readable file size."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 ** 2:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 ** 2):.1f} MB"

    @property
    def icon(self) -> str:
        """Bootstrap icon class based on file type."""
        icons = {"pdf": "bi-file-earmark-pdf", "docx": "bi-file-earmark-word", "txt": "bi-file-earmark-text"}
        return icons.get(self.file_type, "bi-file-earmark")

    def __repr__(self) -> str:
        return f"<Document {self.original_filename}>"
