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
from models.morphology import MorphologyResult
from services.preprocessing_service import PreprocessingService
from services.morphology_service import MorphologyService

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
    def run_morphology(document_id: int) -> bool:
        """
        Runs the morphology phase for a document.
        Saves results to the MorphologyResult model.
        Requires PreprocessingResult to exist.
        """
        logger.info(f"Starting NLP Morphology for Document {document_id}")
        
        # 1. Fetch preprocessed tokens
        prep_result = PreprocessingResult.query.filter_by(document_id=document_id).first()
        if not prep_result or not prep_result.tokens_json:
            logger.error(f"Cannot run morphology: Preprocessing results not found for Document {document_id}")
            return False
            
        try:
            tokens = json.loads(prep_result.tokens_json)
            
            # 2. Run morphology service
            results = MorphologyService.run_morphology(tokens)
            
            # 3. Store in database
            morph_result = MorphologyResult.query.filter_by(document_id=document_id).first()
            if not morph_result:
                morph_result = MorphologyResult(
                    document_id=document_id,
                    preprocessing_result_id=prep_result.id
                )
                db.session.add(morph_result)
                
            morph_result.stemmed_tokens_json = json.dumps(results["stemmed_tokens"])
            morph_result.lemmatized_tokens_json = json.dumps(results["lemmatized_tokens"])
            morph_result.morphology_pairs_json = json.dumps(results["morphology_pairs"])
            morph_result.unique_stems = results["unique_stems"]
            morph_result.unique_lemmas = results["unique_lemmas"]
            morph_result.stem_count = results["stem_count"]
            morph_result.lemma_count = results["lemma_count"]
            morph_result.original_vocabulary_size = results["original_vocabulary_size"]
            morph_result.stemmed_vocabulary_size = results["stemmed_vocabulary_size"]
            morph_result.lemmatized_vocabulary_size = results["lemmatized_vocabulary_size"]
            morph_result.vocabulary_reduction_percentage = results["vocabulary_reduction_percentage"]
            
            db.session.commit()
            logger.info(f"Successfully processed morphology for Document {document_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Failed to process morphology for Document {document_id}: {str(e)}")
            return False
            
    @staticmethod
    def run_statistical_analysis(document_id: int) -> bool:
        """Placeholder for Phase 5: Statistical NLP"""
        logger.info(f"Statistical analysis skipped - Phase 5 Placeholder")
        return True
        
    @staticmethod
    def run_syntax_analysis(document_id: int) -> bool:
        """Placeholder for Phase 6: Syntax Analysis"""
        logger.info(f"Syntax analysis skipped - Phase 6 Placeholder")
        return True
        
    @staticmethod
    def run_semantic_analysis(document_id: int) -> bool:
        """Placeholder for Phase 7: Semantic Analysis"""
        logger.info(f"Semantic analysis skipped - Phase 7 Placeholder")
        return True
        
    @staticmethod
    def run_pragmatic_analysis(document_id: int) -> bool:
        """Placeholder for Phase 8: Pragmatics"""
        logger.info(f"Pragmatic analysis skipped - Phase 8 Placeholder")
        return True

    @staticmethod
    def run_all(document_id: int) -> bool:
        """
        Run the complete NLP pipeline (Preprocessing + Future Phases).
        """
        # Step 1: Preprocessing (Phase 3)
        if not NLPPipeline.run_preprocessing(document_id):
            return False
            
        # Step 2: Morphology (Phase 4)
        if not NLPPipeline.run_morphology(document_id):
            return False
            
        # Step 3: Statistical NLP (Phase 5)
        NLPPipeline.run_statistical_analysis(document_id)
        
        # Step 4: Syntax (Phase 6)
        NLPPipeline.run_syntax_analysis(document_id)
        
        # Step 5: Semantic (Phase 7)
        NLPPipeline.run_semantic_analysis(document_id)
        
        # Step 6: Pragmatic (Phase 8)
        NLPPipeline.run_pragmatic_analysis(document_id)
        
        return True
