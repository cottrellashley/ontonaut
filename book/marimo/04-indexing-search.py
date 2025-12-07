"""Ontonaut Indexing & Search System"""

import marimo

__generated_with = "0.18.3"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
    # 🔍 Ontonaut Indexing & Search System

    A powerful codebase indexing system for registering types with metadata
    and enabling intelligent code search.

    **Key Features:**
    - 🏷️ Custom tag taxonomies
    - 📚 Automatic metadata extraction
    - 🔎 Powerful search capabilities
    - 🔒 Thread-safe registry
    - 🤖 AI agent integration ready
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 1. Define Your Tag Taxonomy
    """
    )
    return


@app.cell
def _():
    from ontonaut import IndexTag

    class ProjectTags(IndexTag):
        """Custom tags for our project."""

        DATABASE = "database"
        API = "api"
        SERVICE = "service"
        UTIL = "util"
        MODEL = "model"
        DEPRECATED = "deprecated"

    return (ProjectTags,)


@app.cell
def _(mo):
    mo.md(
        """
    ## 2. Register Types with Metadata
    """
    )
    return


@app.cell
def _(ProjectTags):
    from ontonaut import index_type

    @index_type(
        tags=[ProjectTags.DATABASE, ProjectTags.MODEL],
        instructions="Primary user model",
    )
    class User:
        """User model for authentication and profile management."""

        def __init__(self, username: str, email: str):
            self.username = username
            self.email = email
            self._is_active = True

        def authenticate(self, password: str) -> bool:
            """
            Authenticate user with password.

            Args:
                password: User password

            Returns:
                True if authentication successful
            """
            # Simplified authentication
            return len(password) > 8

        def deactivate(self) -> None:
            """Deactivate user account."""
            self._is_active = False

        @property
        def is_active(self) -> bool:
            """Check if user account is active."""
            return self._is_active

        @property
        def display_name(self) -> str:
            """Get user's display name."""
            return f"@{self.username}"

        @classmethod
        def create_admin(cls, username: str) -> "User":
            """Create an admin user."""
            return cls(username, f"{username}@admin.local")

    return User, index_type


@app.cell
def _(ProjectTags, index_type):
    @index_type(
        tags=[ProjectTags.API, ProjectTags.SERVICE],
        instructions="REST API for user management",
    )
    class UserService:
        """Service layer for user operations."""

        def __init__(self, db_connection):
            self.db = db_connection

        def create_user(self, username: str, email: str) -> dict:
            """
            Create a new user account.

            Args:
                username: Unique username
                email: User email address

            Returns:
                Dictionary with user data
            """
            return {"id": 1, "username": username, "email": email}

        def find_user(self, user_id: int) -> dict:
            """
            Find user by ID.

            Args:
                user_id: User identifier

            Returns:
                User data dictionary
            """
            return {"id": user_id}

        def list_users(self, limit: int = 100) -> list:
            """
            List all users.

            Args:
                limit: Maximum number of users to return

            Returns:
                List of user dictionaries
            """
            return []

    return


@app.cell
def _(ProjectTags, index_type):
    @index_type(tags=[ProjectTags.UTIL], instructions="Email validation utilities")
    class EmailValidator:
        """Utility class for email validation."""

        @staticmethod
        def is_valid(email: str) -> bool:
            """
            Check if email is valid.

            Args:
                email: Email address to validate

            Returns:
                True if valid
            """
            return "@" in email and "." in email

        @staticmethod
        def normalize(email: str) -> str:
            """Normalize email to lowercase."""
            return email.lower().strip()

    return


@app.cell
def _(ProjectTags, index_type):
    @index_type(
        tags=[ProjectTags.DEPRECATED], instructions="Use EmailValidator instead"
    )
    class OldEmailChecker:
        """Legacy email validation. DEPRECATED."""

        def check(self, email):
            """Old validation method."""
            return "@" in email

    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 3. Inspect Registered Type Metadata
    """
    )
    return


@app.cell
def _(User):
    from ontonaut import get_registry

    registry = get_registry()
    user_registered = registry.get(User)

    # Display metadata
    metadata_info = {
        "Name": user_registered.name,
        "Module": user_registered.module,
        "Path": user_registered.cls_path,
        "Tags": [str(t) for t in user_registered.tags],
        "Instructions": user_registered.instructions,
        "Docstring": user_registered.docstring,
        "Is Abstract": user_registered.is_abstract,
    }
    return metadata_info, user_registered


@app.cell
def _(metadata_info, mo):
    mo.ui.table(
        [{"Property": k, "Value": str(v)} for k, v in metadata_info.items()],
        label="User Type Metadata",
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Methods
    """
    )
    return


@app.cell
def _(mo, user_registered):
    method_data = []
    for name, info in user_registered.methods.items():
        method_data.append(
            {
                "Method": name,
                "Signature": info["signature"] or "(property)",
                "Classmethod": "✅" if info["is_classmethod"] else "",
                "Staticmethod": "✅" if info["is_staticmethod"] else "",
                "Docstring": (
                    info["docstring"][:60] + "..."
                    if len(info["docstring"]) > 60
                    else info["docstring"]
                ),
            }
        )

    mo.ui.table(method_data, label="Public Methods")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Properties
    """
    )
    return


@app.cell
def _(mo, user_registered):
    prop_data = []
    for name, info in user_registered.properties.items():
        prop_data.append(
            {
                "Property": name,
                "Has Setter": "✅" if info["has_setter"] else "❌",
                "Has Deleter": "✅" if info["has_deleter"] else "❌",
                "Docstring": info["docstring"],
            }
        )

    mo.ui.table(prop_data, label="Properties")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 4. Search the Registry
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Search by Query
    """
    )
    return


@app.cell
def _():
    from ontonaut import search_registry

    # Search for "user" in names and docstrings
    user_results = search_registry("user")
    return search_registry, user_results


@app.cell
def _(mo, user_results):
    mo.md(
        f"""
    Found **{len(user_results)}** types matching 'user':
    """
    )
    return


@app.cell
def _(mo, user_results):
    query_data = []
    for r in user_results:
        query_data.append(
            {
                "Name": r.name,
                "Module": r.module,
                "Tags": ", ".join(str(t) for t in r.tags),
                "Docstring": (
                    r.docstring[:50] + "..." if len(r.docstring) > 50 else r.docstring
                ),
            }
        )

    mo.ui.table(query_data)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Search by Tags
    """
    )
    return


@app.cell
def _(ProjectTags, search_registry):
    # Find all database models
    db_models = search_registry(tags=[ProjectTags.DATABASE])

    # Find all services
    services = search_registry(tags=[ProjectTags.SERVICE])

    # Find deprecated code
    deprecated = search_registry(tags=[ProjectTags.DEPRECATED])
    return db_models, deprecated, services


@app.cell
def _(db_models, deprecated, mo, services):
    mo.md(
        f"""
    **Tag Search Results:**
    - Database Models: {len(db_models)}
    - Services: {len(services)}
    - Deprecated: {len(deprecated)}
    """
    )
    return


@app.cell
def _(deprecated, mo):
    if deprecated:
        mo.callout(
            mo.md(
                f"⚠️ **Deprecated Code Found:**\n\n{deprecated[0].name}: {deprecated[0].instructions}"
            ),
            kind="warn",
        )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Combined Search
    """
    )
    return


@app.cell
def _(ProjectTags, search_registry):
    # Find authentication-related database models
    auth_models = search_registry(query="authentication", tags=[ProjectTags.DATABASE])
    return (auth_models,)


@app.cell
def _(auth_models, mo):
    mo.md(
        f"""
    Found **{len(auth_models)}** authentication-related database models
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 5. Search Methods and Properties
    """
    )
    return


@app.cell
def _(user_registered):
    # Find authentication-related methods
    auth_methods = user_registered.search_methods("auth")
    return auth_methods


@app.cell
def _(search_registry):
    def build_ai_context(query: str) -> str:
        """Build context string for AI from registered types."""
        results = search_registry(query)

        if not results:
            return f"No types found matching '{query}'"

        context = [f"# Codebase Context for: {query}\n"]

        for r in results:
            context.append(f"\n## {r.cls_path}")
            context.append(f"**Tags:** {', '.join(str(t) for t in r.tags)}")
            context.append(f"**Description:** {r.docstring}")

            if r.instructions:
                context.append(f"**Instructions:** {r.instructions}")

            context.append("\n### Methods:")
            for name, info in r.methods.items():
                sig = info["signature"] or "(property)"
                context.append(f"- `{name}{sig}`")
                if info["docstring"]:
                    context.append(f"  - {info['docstring'][:100]}")

            if r.properties:
                context.append("\n### Properties:")
                for name, info in r.properties.items():
                    context.append(f"- `{name}` - {info['docstring'][:60]}")

        return "\n".join(context)

    return (build_ai_context,)


@app.cell
def _(build_ai_context):
    ai_context = build_ai_context("user")
    return (ai_context,)


@app.cell
def _(ai_context, mo):
    mo.md(ai_context)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 7. Summary

    The indexing system provides:

    ✅ **Type Registration** - Decorator or function-based
    ✅ **Automatic Metadata** - Docstrings, methods, properties
    ✅ **Custom Tags** - Flexible categorization
    ✅ **Powerful Search** - Query + tags
    ✅ **Thread-Safe** - Concurrent access
    ✅ **AI-Ready** - Easy context building

    **Use Cases:**
    - 🤖 AI agent code understanding
    - 📚 Documentation generation
    - 🔍 Codebase navigation
    - 🏗️ Architecture analysis
    - ⚠️ Technical debt tracking
    """
    )
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
