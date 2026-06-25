"""
Syntax Model
Persists POS-tagging, constituency parsing, dependency parsing,
HMM/Viterbi demo data, and syntax statistics for a document.
"""

from datetime import datetime, timezone
from app_extensions import db


class SyntaxAnalysisResult(db.Model):
    """Stores full Phase 6 syntax analysis for a document."""

    __tablename__ = "syntax_analysis_results"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── POS Tagging ───────────────────────────────────────────────────────────
    # [{token, tag, description, category}, ...]
    pos_tags_json         = db.Column(db.Text, nullable=True)
    # [{token, tag, description}, ...]  — slim version for future reuse
    syntax_pairs_json     = db.Column(db.Text, nullable=True)
    # {tag: count, ...}  ordered by frequency
    tag_frequency_json    = db.Column(db.Text, nullable=True)

    # ── Parsing ───────────────────────────────────────────────────────────────
    # Nested dict representation of constituency parse tree
    parse_tree_json       = db.Column(db.Text, nullable=True)
    # ASCII art strings for top-N sentences
    parse_tree_text       = db.Column(db.Text, nullable=True)
    # [{token, dep, head, head_pos}, ...] per sentence (first N sentences)
    dependency_json       = db.Column(db.Text, nullable=True)
    # "spacy" | "nltk_fallback"
    dependency_engine     = db.Column(db.String(32), default="none")

    # ── Tag-category counts ───────────────────────────────────────────────────
    noun_count            = db.Column(db.Integer, default=0)
    verb_count            = db.Column(db.Integer, default=0)
    adjective_count       = db.Column(db.Integer, default=0)
    adverb_count          = db.Column(db.Integer, default=0)
    other_count           = db.Column(db.Integer, default=0)
    total_tagged_tokens   = db.Column(db.Integer, default=0)

    # ── Derived metrics ───────────────────────────────────────────────────────
    noun_verb_ratio           = db.Column(db.Float, default=0.0)
    avg_pos_per_sentence      = db.Column(db.Float, default=0.0)
    sentence_complexity_score = db.Column(db.Float, default=0.0)

    # ── Meta ──────────────────────────────────────────────────────────────────
    processed_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationship ──────────────────────────────────────────────────────────
    document_ref = db.relationship(
        "Document",
        backref=db.backref(
            "syntax_result",
            uselist=False,
            lazy="joined",
            cascade="all, delete-orphan",
        ),
    )

    def __repr__(self) -> str:
        return f"<SyntaxAnalysisResult for Document {self.document_id}>"
