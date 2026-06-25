"""
utils/decorators.py
Custom route decorators used across the application.
"""

from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(role: str):
    """
    Decorator that restricts a view to users with a specific role.
    (Placeholder — role column can be added to User model when needed.)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            # Future: check current_user.role == role
            return f(*args, **kwargs)
        return decorated_function
    return decorator
