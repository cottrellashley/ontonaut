"""
Sample codebase for demonstrating the indexing system.

This module contains various types that showcase different features
of the ontonaut indexing system.
"""

from ontonaut import IndexTag, register_type


class ProjectTags(IndexTag):
    """Tags for categorizing our sample codebase."""

    DATABASE = "database"
    API = "api"
    SERVICE = "service"
    UTIL = "util"
    MODEL = "model"
    AUTH = "auth"
    DEPRECATED = "deprecated"


class User:
    """
    User model representing authenticated users in the system.

    This class handles user data, authentication, and authorization.
    Users can have multiple roles and permissions.
    """

    def __init__(self, username: str, email: str, password_hash: str):
        """
        Initialize a user.

        Args:
            username: Unique username
            email: User email address
            password_hash: Hashed password
        """
        self.username = username
        self.email = email
        self._password_hash = password_hash
        self._is_active = True
        self._roles = []

    def authenticate(self, password: str) -> bool:
        """
        Authenticate user with password.

        Args:
            password: Plain text password to verify

        Returns:
            True if authentication successful
        """
        # Simplified - in production use proper password hashing
        return len(password) > 8

    def add_role(self, role: str) -> None:
        """
        Add a role to the user.

        Args:
            role: Role name to add
        """
        if role not in self._roles:
            self._roles.append(role)

    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            role: Role name to check

        Returns:
            True if user has the role
        """
        return role in self._roles

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self._is_active

    @property
    def display_name(self) -> str:
        """Get user's display name."""
        return f"@{self.username}"

    @property
    def roles(self) -> list[str]:
        """Get list of user roles."""
        return self._roles.copy()

    @classmethod
    def create_admin(cls, username: str, email: str) -> "User":
        """
        Create an admin user with default settings.

        Args:
            username: Admin username
            email: Admin email

        Returns:
            New User instance with admin role
        """
        user = cls(username, email, "default_hash")
        user.add_role("admin")
        return user


class UserService:
    """
    Service layer for user-related operations.

    Provides business logic for user creation, retrieval,
    update, and deletion operations.
    """

    def __init__(self, database_connection):
        """
        Initialize user service.

        Args:
            database_connection: Database connection instance
        """
        self.db = database_connection

    def create_user(self, username: str, email: str, password: str) -> dict:
        """
        Create a new user account.

        Args:
            username: Unique username
            email: User email address
            password: User password

        Returns:
            Dictionary with user data including ID

        Raises:
            ValueError: If username or email already exists
        """
        # Simplified implementation
        return {"id": 1, "username": username, "email": email, "created": True}

    def get_user(self, user_id: int) -> dict | None:
        """
        Retrieve user by ID.

        Args:
            user_id: User identifier

        Returns:
            User data dictionary or None if not found
        """
        return {"id": user_id, "username": "example"}

    def update_user(self, user_id: int, **kwargs) -> dict:
        """
        Update user information.

        Args:
            user_id: User identifier
            **kwargs: Fields to update

        Returns:
            Updated user data
        """
        return {"id": user_id, "updated": True, **kwargs}

    def delete_user(self, user_id: int) -> bool:
        """
        Delete user account.

        Args:
            user_id: User identifier

        Returns:
            True if deletion successful
        """
        return True

    def list_users(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """
        List all users with pagination.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of user dictionaries
        """
        return []


class EmailValidator:
    """
    Utility class for email validation and processing.

    Provides static methods for email validation, normalization,
    and domain extraction.
    """

    @staticmethod
    def is_valid(email: str) -> bool:
        """
        Check if email address is valid.

        Args:
            email: Email address to validate

        Returns:
            True if email is valid format

        Example:
            >>> EmailValidator.is_valid("user@example.com")
            True
            >>> EmailValidator.is_valid("invalid")
            False
        """
        return "@" in email and "." in email.split("@")[1]

    @staticmethod
    def normalize(email: str) -> str:
        """
        Normalize email to lowercase and trim whitespace.

        Args:
            email: Email address to normalize

        Returns:
            Normalized email address
        """
        return email.lower().strip()

    @staticmethod
    def get_domain(email: str) -> str:
        """
        Extract domain from email address.

        Args:
            email: Email address

        Returns:
            Domain part of email

        Example:
            >>> EmailValidator.get_domain("user@example.com")
            'example.com'
        """
        return email.split("@")[1] if "@" in email else ""

    @staticmethod
    def is_corporate_email(email: str) -> bool:
        """
        Check if email is from a corporate domain.

        Args:
            email: Email address to check

        Returns:
            True if email is from corporate domain (not common providers)
        """
        common_providers = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}
        domain = EmailValidator.get_domain(email).lower()
        return domain not in common_providers


class Session:
    """
    Session model for tracking authenticated user sessions.

    Each session has a unique token and tracks user activity.
    """

    def __init__(self, user_id: int, token: str):
        """
        Initialize session.

        Args:
            user_id: Associated user ID
            token: Session token
        """
        self.user_id = user_id
        self.token = token
        self._is_valid = True

    def invalidate(self) -> None:
        """Mark session as invalid (logout)."""
        self._is_valid = False

    @property
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        return self._is_valid


class OldEmailChecker:
    """
    Legacy email validation class.

    DEPRECATED: This class is deprecated and will be removed in version 2.0.
    Use EmailValidator instead for all email validation needs.
    """

    def check(self, email: str) -> bool:
        """
        Old validation method.

        DEPRECATED: Use EmailValidator.is_valid() instead.

        Args:
            email: Email to check

        Returns:
            True if valid
        """
        return "@" in email


class AuthenticationService:
    """
    Service for handling authentication operations.

    Manages user login, logout, session creation, and token validation.
    """

    def __init__(self, user_service: UserService):
        """
        Initialize authentication service.

        Args:
            user_service: User service instance
        """
        self.user_service = user_service
        self._sessions = {}

    def login(self, username: str, password: str) -> dict:
        """
        Authenticate user and create session.

        Args:
            username: Username
            password: Password

        Returns:
            Dictionary with session token and user data

        Raises:
            ValueError: If authentication fails
        """
        # Simplified implementation
        return {"token": "abc123", "user_id": 1, "username": username}

    def logout(self, token: str) -> bool:
        """
        Logout user and invalidate session.

        Args:
            token: Session token

        Returns:
            True if logout successful
        """
        if token in self._sessions:
            self._sessions[token].invalidate()
            return True
        return False

    def validate_token(self, token: str) -> bool:
        """
        Validate session token.

        Args:
            token: Session token to validate

        Returns:
            True if token is valid
        """
        return token in self._sessions and self._sessions[token].is_valid

    @property
    def active_sessions(self) -> int:
        """Get count of active sessions."""
        return sum(1 for s in self._sessions.values() if s.is_valid)


# Register all types explicitly
register_type(
    typ=User,
    tags=[ProjectTags.DATABASE, ProjectTags.MODEL, ProjectTags.AUTH],
    instructions="Primary user model for authentication and authorization",
)

register_type(
    typ=UserService,
    tags=[ProjectTags.API, ProjectTags.SERVICE, ProjectTags.AUTH],
    instructions="REST API service for user management operations",
)

register_type(
    typ=EmailValidator,
    tags=[ProjectTags.UTIL],
    instructions="Utilities for email validation and normalization",
)

register_type(
    typ=Session,
    tags=[ProjectTags.DATABASE, ProjectTags.MODEL],
    instructions="Database session model for tracking user sessions",
)

register_type(
    typ=OldEmailChecker,
    tags=[ProjectTags.DEPRECATED],
    instructions="DEPRECATED: Use EmailValidator instead. Will be removed in v2.0",
)

register_type(
    typ=AuthenticationService,
    tags=[ProjectTags.API, ProjectTags.SERVICE, ProjectTags.AUTH],
    instructions="Authentication service handling login, logout, and session management",
)
