"""
routes/upload_routes.py
Upload blueprint – file upload, listing, and deletion.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from services.upload_service import UploadService
from models.document import Document

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")


@upload_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    """File upload page with drag-and-drop interface."""
    if request.method == "POST":
        current_app.logger.info("Upload request received")
        files = request.files.getlist("documents")
        current_app.logger.info(f"Files detected in request: {len(files)} files")
        
        if not files or all(f.filename == "" for f in files):
            current_app.logger.warning("No files were selected in the upload form")
            flash("Please select at least one file.", "warning")
            return redirect(request.url)

        success_count = 0
        for file in files:
            if file.filename == "":
                continue
            
            current_app.logger.info(f"Processing file: {file.filename}")
            try:
                ok, msg, _ = UploadService.save_document(file, current_user.id)
                if ok:
                    success_count += 1
                    current_app.logger.info(f"Successfully processed file: {file.filename}")
                else:
                    current_app.logger.warning(f"Failed to process file {file.filename}: {msg}")
                    flash(msg, "danger")
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                current_app.logger.error(f"Exception during upload processing for {file.filename}:\n{error_trace}")
                flash(f"Server error during upload of {file.filename}", "danger")

        if success_count:
            flash(f"{success_count} file(s) uploaded successfully.", "success")
        
        current_app.logger.info(f"Upload request complete. Redirecting. Success count: {success_count}")
        return redirect(url_for("upload.index"))


    documents = UploadService.get_user_documents(current_user.id)
    return render_template("upload/index.html", documents=documents)


@upload_bp.route("/delete/<int:doc_id>", methods=["POST"])
@login_required
def delete(doc_id: int):
    """Delete a document owned by the current user."""
    document = Document.query.get_or_404(doc_id)
    if document.user_id != current_user.id:
        abort(403)
    ok, msg = UploadService.delete_document(document)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("upload.index"))
