"""
NLP Pipeline Orchestrator
Orchestrates the execution of preprocessing and future NLP modules for a document.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app_extensions import db
from models.document import Document
from models.preprocessing import PreprocessingResult
from models.morphology import MorphologyResult
from models.statistical_nlp import StatisticalAnalysisResult
from models.syntax import SyntaxAnalysisResult
from services.preprocessing_service import PreprocessingService
from services.morphology_service import MorphologyService
from services.statistical_nlp_service import StatisticalNLPService
from services.syntax_service import SyntaxService, HMMViterbiDemoService

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
        """
        Runs Phase 5 Statistical NLP for a document.
        Requires MorphologyResult to exist.
        """
        logger.info(f"Starting Statistical NLP for Document {document_id}")

        morph_result = MorphologyResult.query.filter_by(document_id=document_id).first()
        if not morph_result or not morph_result.lemmatized_tokens_json:
            logger.error(
                f"Cannot run statistical NLP: Morphology results not found for Document {document_id}"
            )
            return False

        prep_result = PreprocessingResult.query.filter_by(document_id=document_id).first()

        try:
            lemmatised_tokens = json.loads(morph_result.lemmatized_tokens_json)
            sentences = (
                json.loads(prep_result.sentences_json)
                if prep_result and prep_result.sentences_json
                else []
            )

            results = StatisticalNLPService.run_analysis(lemmatised_tokens, sentences)

            # Upsert
            stat_result = StatisticalAnalysisResult.query.filter_by(
                document_id=document_id
            ).first()
            if not stat_result:
                stat_result = StatisticalAnalysisResult(document_id=document_id)
                db.session.add(stat_result)

            stat_result.unigram_json            = json.dumps(results["unigrams"])
            stat_result.bigram_json             = json.dumps(results["bigrams"])
            stat_result.trigram_json            = json.dumps(results["trigrams"])
            stat_result.tf_json                 = json.dumps(results["tf"])
            stat_result.tfidf_json              = json.dumps(results["tfidf"])
            stat_result.vocabulary_size         = results["vocabulary_size"]
            stat_result.total_tokens            = results["total_tokens"]
            stat_result.unique_bigrams          = results["unique_bigrams"]
            stat_result.unique_trigrams         = results["unique_trigrams"]
            stat_result.type_token_ratio        = results["type_token_ratio"]
            stat_result.language_model_json     = json.dumps(results["language_model"])
            stat_result.perplexity_score        = results["perplexity_score"]
            stat_result.perplexity_detail_json  = json.dumps(results["perplexity_detail"])
            stat_result.processed_at            = datetime.now(timezone.utc)

            db.session.commit()
            logger.info(f"Successfully ran statistical NLP for Document {document_id}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.exception(
                f"Failed to run statistical NLP for Document {document_id}: {str(e)}"
            )
            return False
        
    @staticmethod
    def run_syntax_analysis(document_id: int) -> bool:
        """
        Runs Phase 6 Syntax Analysis for a document.
        Requires PreprocessingResult to exist.
        """
        logger.info(f"Starting Syntax Analysis for Document {document_id}")

        prep_result = PreprocessingResult.query.filter_by(document_id=document_id).first()
        if not prep_result or not prep_result.sentences_json:
            logger.error(
                f"Cannot run syntax analysis: Preprocessing sentences not found for Document {document_id}"
            )
            return False

        morph_result = MorphologyResult.query.filter_by(document_id=document_id).first()
        tokens = []
        if morph_result and morph_result.lemmatized_tokens_json:
            try:
                tokens = json.loads(morph_result.lemmatized_tokens_json)
            except:
                pass

        try:
            sentences = json.loads(prep_result.sentences_json)
            results = SyntaxService.run_analysis(sentences, tokens)

            stat_result = SyntaxAnalysisResult.query.filter_by(document_id=document_id).first()
            if not stat_result:
                stat_result = SyntaxAnalysisResult(document_id=document_id)
                db.session.add(stat_result)

            stat_result.pos_tags_json = json.dumps(results["pos_tags"])
            stat_result.syntax_pairs_json = json.dumps(results["syntax_pairs"])
            stat_result.tag_frequency_json = json.dumps(results["tag_frequency"])
            stat_result.parse_tree_json = json.dumps(results["parse_tree"])
            stat_result.parse_tree_text = json.dumps(results["parse_tree_text"])
            stat_result.dependency_json = json.dumps(results["dependency"])
            stat_result.dependency_engine = results["dependency_engine"]
            stat_result.noun_count = results["noun_count"]
            stat_result.verb_count = results["verb_count"]
            stat_result.adjective_count = results["adjective_count"]
            stat_result.adverb_count = results["adverb_count"]
            stat_result.other_count = results["other_count"]
            stat_result.total_tagged_tokens = results["total_tokens"]
            stat_result.noun_verb_ratio = results["noun_verb_ratio"]
            stat_result.avg_pos_per_sentence = results["avg_pos_per_sentence"]
            stat_result.sentence_complexity_score = results["sentence_complexity_score"]
            stat_result.processed_at = datetime.now(timezone.utc)

            db.session.commit()
            logger.info(f"Successfully ran syntax analysis for Document {document_id}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.exception(
                f"Failed to run syntax analysis for Document {document_id}: {str(e)}"
            )
            return False
        
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
        if not NLPPipeline.run_statistical_analysis(document_id):
            logger.warning(f"Statistical NLP failed for Document {document_id} – continuing pipeline")
        
        # Step 4: Syntax (Phase 6)
        if not NLPPipeline.run_syntax_analysis(document_id):
            logger.warning(f"Syntax NLP failed for Document {document_id} – continuing pipeline")
        
        # Step 5: Semantic (Phase 7)
        NLPPipeline.run_semantic_analysis(document_id)
        
        # Step 6: Pragmatic (Phase 8)
        NLPPipeline.run_pragmatic_analysis(document_id)
        
        return True
