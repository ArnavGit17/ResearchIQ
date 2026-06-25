"""
Morphology Model
Tracks the morphological analysis outputs (stemming, lemmatization) for a document.
"""

from datetime import datetime, timezone
from app_extensions import db

class MorphologyResult(db.Model):
    """Stores stemming, lemmatization, and morphological stats for a document."""

    __tablename__ = "morphology_results"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    preprocessing_result_id = db.Column(db.Integer, db.ForeignKey("preprocessing_results.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Content arrays
    stemmed_tokens_json = db.Column(db.Text, nullable=True)     # JSON string of stemmed tokens
    lemmatized_tokens_json = db.Column(db.Text, nullable=True)  # JSON string of lemmatized tokens
    
    # Explainable Pairs Mapping (token, stem, lemma, explanations)
    morphology_pairs_json = db.Column(db.Text, nullable=True)
    
    # Basic Stats
    unique_stems = db.Column(db.Integer, default=0)
    unique_lemmas = db.Column(db.Integer, default=0)
    stem_count = db.Column(db.Integer, default=0)
    lemma_count = db.Column(db.Integer, default=0)
    
    # Vocabulary Reduction Metrics
    original_vocabulary_size = db.Column(db.Integer, default=0)
    stemmed_vocabulary_size = db.Column(db.Integer, default=0)
    lemmatized_vocabulary_size = db.Column(db.Integer, default=0)
    vocabulary_reduction_percentage = db.Column(db.Float, default=0.0)
    
    # Meta
    processed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship back to Document
    document_ref = db.relationship("Document", backref=db.backref("morphology_result", uselist=False, lazy="joined", cascade="all, delete-orphan"))
    preprocessing_ref = db.relationship("PreprocessingResult", backref=db.backref("morphology_result", uselist=False))

    def __repr__(self) -> str:
        return f"<MorphologyResult for Document {self.document_id}>"
