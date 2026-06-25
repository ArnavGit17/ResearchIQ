"""
User Model
Handles authentication, password hashing, and Flask-Login integration.
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app_extensions import db


class User(UserMixin, db.Model):
    """Registered user account."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    documents = db.relationship("Document", backref="owner", lazy="dynamic", cascade="all, delete-orphan")

    # ── Password helpers ───────────────────────────────────────────────────────

    def set_password(self, password: str) -> None:
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # ── Statistics ─────────────────────────────────────────────────────────────

    @property
    def document_count(self) -> int:
        return self.documents.count()

    @property
    def analysis_count(self) -> int:
        from models.analysis import Analysis
        from models.document import Document
        doc_ids = [d.id for d in self.documents]
        if not doc_ids:
            return 0
        return Analysis.query.filter(Analysis.document_id.in_(doc_ids)).count()

    @property
    def question_count(self) -> int:
        from models.question import Question
        doc_ids = [d.id for d in self.documents]
        if not doc_ids:
            return 0
        return Question.query.filter(Question.document_id.in_(doc_ids)).count()

    @property
    def summary_count(self) -> int:
        from models.summary import Summary
        doc_ids = [d.id for d in self.documents]
        if not doc_ids:
            return 0
        return Summary.query.filter(Summary.document_id.in_(doc_ids)).count()

    def __repr__(self) -> str:
        return f"<User {self.username}>"
