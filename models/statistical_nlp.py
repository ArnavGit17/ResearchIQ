"""
Statistical NLP Model
Persists n-gram, TF, TF-IDF, vocabulary, and perplexity outputs for a document.
"""

from datetime import datetime, timezone
from app_extensions import db


class StatisticalAnalysisResult(db.Model):
    """Stores n-gram frequencies, TF, TF-IDF, and perplexity for a document."""

    __tablename__ = "statistical_analysis_results"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── N-gram JSON arrays (top-N entries: [[term, freq], ...]) ──────────────
    unigram_json   = db.Column(db.Text, nullable=True)   # top-200 unigrams
    bigram_json    = db.Column(db.Text, nullable=True)   # top-100 bigrams
    trigram_json   = db.Column(db.Text, nullable=True)   # top-50 trigrams

    # ── TF / TF-IDF (top-N entries: [[term, score], ...]) ────────────────────
    tf_json        = db.Column(db.Text, nullable=True)   # top-100 by TF
    tfidf_json     = db.Column(db.Text, nullable=True)   # top-100 by TF-IDF

    # ── Vocabulary / corpus statistics ────────────────────────────────────────
    vocabulary_size      = db.Column(db.Integer, default=0)
    total_tokens         = db.Column(db.Integer, default=0)
    unique_bigrams       = db.Column(db.Integer, default=0)
    unique_trigrams      = db.Column(db.Integer, default=0)
    type_token_ratio     = db.Column(db.Float,   default=0.0)

    # ── Language model probabilities (sample sentence) ────────────────────────
    # JSON: {"sentence": str, "tokens": [...], "unigram_probs": {...},
    #         "bigram_probs": {...}, "trigram_probs": {...}}
    language_model_json  = db.Column(db.Text, nullable=True)

    # ── Perplexity ────────────────────────────────────────────────────────────
    perplexity_score     = db.Column(db.Float,   default=0.0)
    # JSON: {"sentence": str, "log_probs": [...], "formula": str,
    #        "interpretation": str}
    perplexity_detail_json = db.Column(db.Text, nullable=True)

    # ── Meta ──────────────────────────────────────────────────────────────────
    processed_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    document_ref = db.relationship(
        "Document",
        backref=db.backref(
            "statistical_result",
            uselist=False,
            lazy="joined",
            cascade="all, delete-orphan",
        ),
    )

    def __repr__(self) -> str:
        return f"<StatisticalAnalysisResult for Document {self.document_id}>"
