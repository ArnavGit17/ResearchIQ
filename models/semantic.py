"""
Semantic Model
Persists WordNet analysis, Word Sense Disambiguation, and semantic similarity metrics.
"""

from datetime import datetime, timezone
from app_extensions import db


class SemanticAnalysisResult(db.Model):
    """Stores full Phase 7 semantic analysis for a document."""

    __tablename__ = "semantic_analysis_results"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── WordNet Storage ───────────────────────────────────────────────────────
    # Word -> list of synonyms, antonyms, hypernyms, hyponyms
    synonyms_json         = db.Column(db.Text, nullable=True)
    antonyms_json         = db.Column(db.Text, nullable=True)
    hypernyms_json        = db.Column(db.Text, nullable=True)
    hyponyms_json         = db.Column(db.Text, nullable=True)

    # Reusable semantic pairs: [{"word": "car", "synonyms": [...], "hypernyms": [...]}, ...]
    semantic_pairs_json   = db.Column(db.Text, nullable=True)

    # ── Similarity & Disambiguation ───────────────────────────────────────────
    # Pairs of words and their Path/WUP similarity scores
    semantic_similarity_json = db.Column(db.Text, nullable=True)
    
    # Word Sense Disambiguation (Lesk) results: 
    # [{"word": "bank", "context": "...", "sense": "...", "reason": "..."}, ...]
    word_senses_json      = db.Column(db.Text, nullable=True)

    # ── Analytics & Metrics ───────────────────────────────────────────────────
    ambiguity_score       = db.Column(db.Float, default=0.0)

    # ── Meta ──────────────────────────────────────────────────────────────────
    processed_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationship ──────────────────────────────────────────────────────────
    document_ref = db.relationship(
        "Document",
        backref=db.backref(
            "semantic_result",
            uselist=False,
            lazy="joined",
            cascade="all, delete-orphan",
        ),
    )

    def __repr__(self) -> str:
        return f"<SemanticAnalysisResult for Document {self.document_id}>"
