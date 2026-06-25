import os
import logging
import fitz  # PyMuPDF
import docx
from typing import Dict, Any, Optional

from app_extensions import db
from models.document import Document
from services.pre_cleaning_service import PreCleaningService
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Handles text extraction from uploaded files (PDF, DOCX, TXT),
    cleans the text, and calculates statistics.
    """

    @staticmethod
    def process_document(document_id: int, filepath: str) -> bool:
        """
        Extracts text, cleans it, calculates stats, and updates the database.
        Returns True if successful, False otherwise.
        """
        doc = db.session.get(Document, document_id)
        if not doc:
            logger.error(f"Document {document_id} not found for processing.")
            return False

        doc.processing_status = "processing"
        db.session.commit()

        raw_text = ""
        try:
            # 1. Extraction
            if doc.file_type == "pdf":
                raw_text = DocumentProcessor._extract_from_pdf(filepath)
            elif doc.file_type == "docx":
                raw_text = DocumentProcessor._extract_from_docx(filepath)
            elif doc.file_type == "txt":
                raw_text = DocumentProcessor._extract_from_txt(filepath)
            else:
                raise ValueError(f"Unsupported file type: {doc.file_type}")

            # 2. Cleaning
            cleaned_text = PreCleaningService.clean_text(raw_text)

            # 3. Statistics
            stats = PreCleaningService.calculate_statistics(cleaned_text)

            # 4. Database Update
            doc.raw_text = raw_text
            doc.cleaned_text = cleaned_text
            doc.word_count = stats["word_count"]
            doc.sentence_count = stats["sentence_count"]
            doc.character_count = stats["character_count"]
            
            doc.processing_status = "success"
            doc.status = "ready"
            doc.processed_at = datetime.now(timezone.utc)
            db.session.commit()
            
            logger.info(f"Successfully processed document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {str(e)}")
            doc.processing_status = "failed"
            doc.status = "error"
            db.session.commit()
            return False

    @staticmethod
    def _extract_from_pdf(filepath: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        text = []
        try:
            with fitz.open(filepath) as pdf_doc:
                for page in pdf_doc:
                    text.append(page.get_text())
            return "\n".join(text)
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise

    @staticmethod
    def _extract_from_docx(filepath: str) -> str:
        """Extract text from DOCX using python-docx."""
        text = []
        try:
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text.append(para.text)
            return "\n".join(text)
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            raise

    @staticmethod
    def _extract_from_txt(filepath: str) -> str:
        """Extract text from TXT with UTF-8 encoding."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback for ISO-8859-1 if UTF-8 fails
            with open(filepath, "r", encoding="iso-8859-1") as f:
                return f.read()
        except Exception as e:
            logger.error(f"TXT extraction error: {e}")
            raise
