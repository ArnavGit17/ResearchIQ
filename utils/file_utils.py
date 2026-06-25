"""
utils/file_utils.py
File validation and path helpers for the upload system.
"""

import os
import uuid
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def allowed_file(filename: str) -> bool:
    """Return True if the file extension is in the allowed set."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_file_extension(filename: str) -> str:
    """Extract and return the lowercase file extension (without dot)."""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def generate_unique_filename(original_filename: str) -> str:
    """
    Create a collision-safe stored filename.
    Pattern: <uuid4>_<secure_original>
    """
    ext = get_file_extension(original_filename)
    safe_name = secure_filename(original_filename)
    unique_prefix = uuid.uuid4().hex
    return f"{unique_prefix}_{safe_name}"


def format_file_size(size_bytes: int) -> str:
    """Convert raw bytes to a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 ** 2):.1f} MB"


def ensure_upload_dir(upload_folder: str) -> None:
    """Create the uploads directory if it does not exist."""
    os.makedirs(upload_folder, exist_ok=True)
