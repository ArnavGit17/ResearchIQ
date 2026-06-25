"""
app_extensions.py
Shared Flask extensions instantiated here to avoid circular imports.
Import `db`, `login_manager`, and `csrf` from this module everywhere.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# SQLAlchemy instance — bound to the app in create_app()
db = SQLAlchemy()

# Flask-Login instance
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

# CSRF protection — registers csrf_token() Jinja2 global and validates POST tokens
csrf = CSRFProtect()
