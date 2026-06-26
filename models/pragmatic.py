from datetime import datetime, timezone
from app_extensions import db


class PragmaticAnalysisResult(db.Model):
    """
    Phase 8: Pragmatics & Discourse Intelligence
    Stores coreference, context entities, intent, discourse relations, etc.
    """
    __tablename__ = 'pragmatic_analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Pragmatic Data
    coreference_json = db.Column(db.Text, nullable=True)          # e.g., mapping pronouns to entities
    discourse_relations_json = db.Column(db.Text, nullable=True)  # e.g., Cause, Contrast, Addition
    context_entities_json = db.Column(db.Text, nullable=True)     # e.g., flow of entities across document
    intent_classification_json = db.Column(db.Text, nullable=True)# e.g., Statement, Question, Suggestion
    entity_timeline_json = db.Column(db.Text, nullable=True)      # e.g., chronological mapping of mentions
    discourse_markers_json = db.Column(db.Text, nullable=True)    # e.g., "however", "therefore"
    ambiguity_resolution_json = db.Column(db.Text, nullable=True) # e.g., how ambiguous words were fixed contextually
    confidence_scores_json = db.Column(db.Text, nullable=True)    # confidence per inference
    pragmatic_summary_json = db.Column(db.Text, nullable=True)    # high-level discourse summary

    processed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PragmaticAnalysisResult Doc:{self.document_id}>"
