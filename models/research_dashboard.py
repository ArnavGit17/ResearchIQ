"""
Phase 9B: Research Dashboard Model
Caches computed dashboard aggregation metrics to avoid recalculation.
"""

from datetime import datetime, timezone
from app_extensions import db


class ResearchDashboardResult(db.Model):
    """
    Stores aggregated Research Intelligence Dashboard data for a document.
    All fields are computed FROM previous phase outputs — no new NLP is run.
    """
    __tablename__ = 'research_dashboard_results'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey('documents.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )

    # ── Computed Analytics ────────────────────────────────────────────────────
    health_score_json        = db.Column(db.Text, nullable=True)   # composite + subscores
    readability_json         = db.Column(db.Text, nullable=True)   # avg sent/word length, difficulty
    topic_analysis_json      = db.Column(db.Text, nullable=True)   # top topics from TF-IDF clusters
    complexity_json          = db.Column(db.Text, nullable=True)   # perplexity, POS dist, ambiguity
    executive_summary_json   = db.Column(db.Text, nullable=True)   # synthesized summary
    pipeline_timeline_json   = db.Column(db.Text, nullable=True)   # phase timestamps
    entity_intelligence_json = db.Column(db.Text, nullable=True)   # categorized entities
    research_insights_json   = db.Column(db.Text, nullable=True)   # keywords, concepts, lexical stats
    document_overview_json   = db.Column(db.Text, nullable=True)   # doc stats

    processed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Relationship ──────────────────────────────────────────────────────────
    document_ref = db.relationship(
        'Document',
        backref=db.backref(
            'dashboard_result',
            uselist=False,
            lazy='joined',
            cascade='all, delete-orphan'
        )
    )

    def __repr__(self):
        return f'<ResearchDashboardResult Doc:{self.document_id}>'
