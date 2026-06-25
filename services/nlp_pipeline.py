"""
NLP Pipeline Orchestrator
Orchestrates the execution of preprocessing and future NLP modules for a document.
"""

import json
import logging
from typing import Dict, Any, Optional

from app_extensions import db
from models.document import Document
from models.preprocessing import PreprocessingResult
from services.preprocessing_service import PreprocessingService

logger = logging.getLogger(__name__)


class NLPPipeline:
    """Orchestrates the NLP analysis flow for a document."""

    @staticmethod
    def run_preprocessing(document_id: int) -> bool:
        """
        Runs the preprocessing phase for a document.
        Saves results to the PreprocessingResult model.
        Returns True if successful, False otherwise.
        """
        document = db.session.get(Document, document_id)
        if not document or not document.cleaned_text:
            logger.error(f"Cannot run preprocessing: Document {document_id} not found or missing text.")
            return False
            
        logger.info(f"Starting NLP Preprocessing for Document {document_id}")
        
        try:
            # 1. Run the NLP service functions
            results = PreprocessingService.run_preprocessing(document.cleaned_text)
            
            # 2. Store in database
            prep_result = PreprocessingResult.query.filter_by(document_id=document_id).first()
            if not prep_result:
                prep_result = PreprocessingResult(document_id=document_id)
                db.session.add(prep_result)
                
            prep_result.token_count = results["token_count"]
            prep_result.sentence_count = results["sentence_count"]
            prep_result.unique_token_count = results["unique_token_count"]
            prep_result.vocabulary_size = results["vocabulary_size"]
            prep_result.average_sentence_length = results["average_sentence_length"]
            prep_result.normalized_text = results["normalized_text"]
            prep_result.tokens_json = json.dumps(results["tokens"])
            prep_result.sentences_json = json.dumps(results["sentences"])
            
            db.session.commit()
            logger.info(f"Successfully processed Document {document_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Failed to preprocess Document {document_id}: {str(e)}")
            return False

    @staticmethod
    def run_all(document_id: int) -> bool:
        """
        Run the complete NLP pipeline (Preprocessing + Future Phases).
        Currently only runs preprocessing.
        """
        # Step 1: Preprocessing (Phase 3)
        success = NLPPipeline.run_preprocessing(document_id)
        if not success:
            return False
            
        # Step 2: Morphology (Phase 4 Placeholder)
        # success = NLPPipeline.run_morphology(document_id)
        
        # Step 3: Syntax (Phase 5 Placeholder)
        # ...
        
        return True
