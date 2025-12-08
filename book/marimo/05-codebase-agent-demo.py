"""CodebaseAgent Demo - Ask Questions About Your Codebase"""

import marimo

__generated_with = "0.18.3"
app = marimo.App()


@app.cell
def _():
    return


@app.cell
def _():
    # Register sample codebase types for the agent to search
    from ontonaut import IndexTag, register_type

    class ProjectTags(IndexTag):
        """Tags for categorizing our sample codebase."""

        DATABASE = "database"
        API = "api"
        SERVICE = "service"
        UTIL = "util"
        AUTH = "auth"

    # Define types
    class User:
        """User model representing authenticated users in the system."""

        def authenticate(self, password: str) -> bool:
            """Authenticate user with password."""
            return len(password) > 8

        @property
        def is_active(self) -> bool:
            """Check if user account is active."""
            return True

    class UserService:
        """Service layer for user-related operations."""

        def create_user(self, username: str, email: str, password: str) -> dict:
            """Create a new user account."""
            return {"id": 1, "username": username, "email": email}

        def get_user(self, user_id: int) -> dict | None:
            """Retrieve user by ID."""
            return {"id": user_id}

    class EmailValidator:
        """Utility class for email validation and processing."""

        @staticmethod
        def is_valid(email: str) -> bool:
            """Check if email address is valid."""
            return "@" in email and "." in email

    # Register types explicitly
    register_type(
        typ=User,
        tags=[ProjectTags.DATABASE, ProjectTags.AUTH],
        instructions="Primary user model for authentication",
    )

    register_type(
        typ=UserService,
        tags=[ProjectTags.API, ProjectTags.SERVICE],
        instructions="REST API service for user management",
    )

    register_type(
        typ=EmailValidator,
        tags=[ProjectTags.UTIL],
        instructions="Email validation utilities",
    )
    return


@app.cell
def _():
    # Setup: Load API key and initialize OpenAI client
    import os

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("⚠️ OPENAI_API_KEY not found in .env file")

    # Initialize OpenAI client
    import openai

    ai_client = openai.OpenAI(api_key=api_key)

    # Create the CodebaseAgent
    from ontonaut import CodebaseAgent

    agent = CodebaseAgent(ai_client=ai_client, theme="dark")
    return (agent,)


@app.cell
def _():
    # The agent is ready to use!
    return


@app.cell
def _(agent):
    agent
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
