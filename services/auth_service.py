"""
services/auth_service.py
Business logic for user registration and login.
"""

from app_extensions import db
from models.user import User


class AuthService:
    """Encapsulates authentication operations."""

    @staticmethod
    def register_user(username: str, email: str, password: str) -> tuple[bool, str, User | None]:
        """
        Create a new user account.

        Returns:
            (success: bool, message: str, user: User | None)
        """
        # Check uniqueness
        if User.query.filter_by(username=username).first():
            return False, "Username is already taken.", None
        if User.query.filter_by(email=email).first():
            return False, "Email address is already registered.", None

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return True, "Account created successfully. Please log in.", user

    @staticmethod
    def authenticate_user(email: str, password: str) -> tuple[bool, str, User | None]:
        """
        Validate credentials for login.

        Returns:
            (success: bool, message: str, user: User | None)
        """
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return False, "Invalid email or password.", None
        return True, "Login successful.", user
