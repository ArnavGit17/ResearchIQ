"""
routes/settings_routes.py
Settings blueprint – account and application preferences.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app_extensions import db

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    """User settings page."""
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            new_username = request.form.get("username", "").strip()
            if new_username and new_username != current_user.username:
                from models.user import User
                existing = User.query.filter_by(username=new_username).first()
                if existing:
                    flash("Username already taken.", "danger")
                else:
                    current_user.username = new_username
                    db.session.commit()
                    flash("Profile updated successfully.", "success")

        elif action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw     = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            if not current_user.check_password(current_pw):
                flash("Current password is incorrect.", "danger")
            elif len(new_pw) < 8:
                flash("New password must be at least 8 characters.", "danger")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "danger")
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash("Password changed successfully.", "success")

        return redirect(url_for("settings.index"))

    return render_template("settings/index.html")
