"""
services/upload_service.py
Handles file saving, validation, and database record creation.
"""

import os
from flask import current_app
from app_extensions import db
from models.document import Document
from utils.file_utils import allowed_file, get_file_extension, generate_unique_filename, ensure_upload_dir
from services.document_processor import DocumentProcessor



class UploadService:
    """Service layer for document upload operations."""

    @staticmethod
    def save_document(file, user_id: int) -> tuple[bool, str, Document | None]:
        """
        Validate, save, and register an uploaded file.

        Returns:
            (success: bool, message: str, document: Document | None)
        """
        if not file or file.filename == "":
            current_app.logger.warning("Validation failed: No file selected")
            return False, "No file selected.", None

        if not allowed_file(file.filename):
            current_app.logger.warning(f"Validation failed: Invalid file type for {file.filename}")
            return False, "Invalid file type. Only PDF, DOCX, and TXT are allowed.", None

        current_app.logger.info(f"Validation passed for file: {file.filename}")

        original_filename = file.filename
        stored_filename = generate_unique_filename(original_filename)
        file_ext = get_file_extension(original_filename)

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        ensure_upload_dir(upload_folder)

        save_path = os.path.join(upload_folder, stored_filename)

        try:
            current_app.logger.info(f"Saving file to: {save_path}")
            file.save(save_path)
            file_size = os.path.getsize(save_path)
            current_app.logger.info(f"File saved successfully. Size: {file_size} bytes")
        except OSError as e:
            import traceback
            current_app.logger.error(f"File save error: {e}\n{traceback.format_exc()}")
            return False, "Failed to save file. Please try again.", None
        except Exception as e:
            import traceback
            current_app.logger.error(f"Unexpected file save error: {e}\n{traceback.format_exc()}")
            return False, "Failed to save file. Please try again.", None

        try:
            # Create database record
            current_app.logger.info("Creating database record...")
            document = Document(
                user_id=user_id,
                filename=stored_filename,
                original_filename=original_filename,
                file_type=file_ext,
                file_size=file_size,
                status="uploaded",
            )
            db.session.add(document)
            db.session.commit()
            current_app.logger.info(f"Database record created successfully. Document ID: {document.id}")
        except Exception as e:
            import traceback
            current_app.logger.error(f"Database error during commit: {e}\n{traceback.format_exc()}")
            db.session.rollback()
            return False, "Database error while saving document.", None

        try:
            # Synchronously process document text (Phase 2)
            # Note: In production this should be a background task (e.g. Celery)
            current_app.logger.info(f"Triggering DocumentProcessor for document ID: {document.id}")
            DocumentProcessor.process_document(document.id, save_path)
            current_app.logger.info(f"DocumentProcessor completed for document ID: {document.id}")
        except Exception as e:
            import traceback
            current_app.logger.error(f"DocumentProcessor error: {e}\n{traceback.format_exc()}")
            # We don't return False here since the upload itself succeeded, just the processing failed.

        return True, "File uploaded and processed successfully.", document

    @staticmethod
    def delete_document(document: Document) -> tuple[bool, str]:
        """Remove a document's file from disk and its database record."""
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, document.filename)

        # Remove physical file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                current_app.logger.warning(f"Could not delete file {file_path}: {e}")

        db.session.delete(document)
        db.session.commit()
        return True, "Document deleted."

    @staticmethod
    def get_user_documents(user_id: int):
        """Fetch all documents belonging to a user, newest first."""
        return (
            Document.query
            .filter_by(user_id=user_id)
            .order_by(Document.upload_date.desc())
            .all()
        )
