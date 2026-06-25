"""
ResearchIQ - Application Configuration
Supports multiple environments: Development, Testing, Production
"""

import os
from datetime import timedelta

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with shared settings."""

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "researchiq-dev-secret-key-change-in-production")
    WTF_CSRF_ENABLED = True

    # ── Database ──────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'researchiq.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Session ───────────────────────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # ── File Upload ───────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

    # ── Application Meta ──────────────────────────────────────────────────────
    APP_NAME = "ResearchIQ"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Explainable Multi-Level NLP Research Intelligence Platform"


class DevelopmentConfig(Config):
    """Development configuration — verbose logging, debug mode enabled."""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set True to log all SQL queries


class TestingConfig(Config):
    """Testing configuration — in-memory SQLite, CSRF disabled."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration — strict security, no debug."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Requires HTTPS


# Configuration map used by the application factory
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
