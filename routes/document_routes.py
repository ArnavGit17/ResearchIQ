"""
routes/document_routes.py
Document management and preview routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.document import Document
from app_extensions import db

document_bp = Blueprint("document_bp", __name__, url_prefix="/documents")


@document_bp.route("/")
@login_required
def index():
    """Document management dashboard."""
    query = Document.query.filter_by(user_id=current_user.id)
    
    # Filter by type
    file_type = request.args.get('type')
    if file_type and file_type in ['pdf', 'docx', 'txt']:
        query = query.filter_by(file_type=file_type)
        
    # Search by filename
    search = request.args.get('q')
    if search:
        query = query.filter(Document.original_filename.ilike(f'%{search}%'))
        
    # Sort
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'oldest':
        query = query.order_by(Document.upload_date.asc())
    elif sort_by == 'largest':
        query = query.order_by(Document.file_size.desc())
    else:
        query = query.order_by(Document.upload_date.desc())
        
    documents = query.all()
    
    return render_template("documents/index.html", documents=documents, current_filter=file_type, current_sort=sort_by, search_query=search)


@document_bp.route("/<int:doc_id>")
@login_required
def preview(doc_id):
    """Document preview page."""
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    
    # Get a 2000 character preview
    preview_text = doc.cleaned_text[:2000] if doc.cleaned_text else ""
    if doc.cleaned_text and len(doc.cleaned_text) > 2000:
        preview_text += "\n\n... [Text truncated for preview] ..."
        
    return render_template("documents/preview.html", document=doc, preview_text=preview_text)
