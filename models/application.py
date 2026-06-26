from datetime import datetime, timezone
from app_extensions import db

class ApplicationAnalysisResult(db.Model):
    """
    Phase 9A: Application Layer
    Stores results from practical applications like NER, Keywords, Summarization, QA, and Search.
    """
    __tablename__ = 'application_analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    entities_json = db.Column(db.Text, nullable=True)
    keywords_json = db.Column(db.Text, nullable=True)
    summary_json = db.Column(db.Text, nullable=True)
    qa_history_json = db.Column(db.Text, nullable=True)
    semantic_search_json = db.Column(db.Text, nullable=True)
    application_statistics_json = db.Column(db.Text, nullable=True)
    confidence_scores_json = db.Column(db.Text, nullable=True)

    processed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ApplicationAnalysisResult Doc:{self.document_id}>"
