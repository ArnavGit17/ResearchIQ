"""
app.py
ResearchIQ – Application Factory
Initialises Flask, extensions, blueprints, and the database.
"""

import os
from flask import Flask, render_template, redirect, url_for

from app_extensions import db, login_manager, csrf
from config import config_map


def create_app(env: str | None = None) -> Flask:
    """
    Application factory.

    Args:
        env: One of 'development' | 'testing' | 'production'.
             Defaults to the FLASK_ENV environment variable or 'development'.

    Returns:
        Configured Flask application instance.
    """
    env = env or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map.get(env, config_map["default"]))

    # ── Ensure required directories exist ─────────────────────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)

    # ── Initialise extensions ──────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader required by Flask-Login
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # ── Register blueprints ────────────────────────────────────────────────────
    from routes.auth_routes      import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.upload_routes import upload_bp
    from routes.nlp_routes import nlp_bp
    from routes.analytics_routes import analytics_bp
    from routes.settings_routes import settings_bp
    from routes.document_routes import document_bp
    from routes.api_routes import api_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(nlp_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(api_bp)


    # ── Root redirect ──────────────────────────────────────────────────────────
    @app.route("/")
    def root():
        return redirect(url_for("dashboard.index"))

    # ── Error handlers ─────────────────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # ── Register custom Jinja2 filters ────────────────────────────────────────
    import json as _json

    def _fromjson(value, default=None):
        """Parse a JSON string into a Python object. Returns default on failure."""
        if not value:
            return default if default is not None else []
        try:
            return _json.loads(value)
        except (ValueError, TypeError):
            return default if default is not None else []

    app.jinja_env.filters["fromjson"] = _fromjson

    # ── Create database tables ─────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=flask_app.config.get("DEBUG", True),
    )
