"""
Demo: Iterative CodebaseAgent

This demo shows the intelligent iterative agent in action.
The agent will plan, search, and synthesize information to answer your questions.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("⚠️  OPENAI_API_KEY not found in .env file")
    print("Please create a .env file with your OpenAI API key:")
    print("OPENAI_API_KEY=sk-...")
    sys.exit(1)

# Initialize OpenAI client
import openai

client = openai.OpenAI(api_key=api_key)

# Register some example types
from ontonaut import IndexTag, register_type


class ProjectTags(IndexTag):
    """Custom tags for our project."""

    DATABASE = "database"
    API = "api"
    SERVICE = "service"
    AUTH = "authentication"
    UTIL = "utility"


# Example: User model
class User:
    """User model for authentication and authorization."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.is_active = True

    def authenticate(self, password: str) -> bool:
        """Verify user password."""
        # In real app, use proper password hashing
        return self.password == password

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False


# Example: Authentication service
class AuthService:
    """Service for handling user authentication."""

    def login(self, email: str, password: str) -> dict:
        """
        Authenticate user and create session.

        Args:
            email: User's email address
            password: User's password

        Returns:
            Dictionary with login result and session token
        """
        # Implementation would go here
        return {"success": True, "token": "abc123"}

    def logout(self, token: str) -> bool:
        """Invalidate user session."""
        return True

    def validate_token(self, token: str) -> bool:
        """Check if session token is valid."""
        return True


# Example: Email service
class EmailService:
    """Service for sending emails."""

    def send_welcome_email(self, user_email: str) -> bool:
        """Send welcome email to new user."""
        print(f"Sending welcome email to {user_email}")
        return True

    def send_password_reset(self, user_email: str) -> bool:
        """Send password reset email."""
        print(f"Sending password reset to {user_email}")
        return True


# Register all types with tags
register_type(
    typ=User,
    tags=[ProjectTags.DATABASE, ProjectTags.AUTH],
    instructions="Main user model with authentication methods",
)

register_type(
    typ=AuthService,
    tags=[ProjectTags.SERVICE, ProjectTags.AUTH, ProjectTags.API],
    instructions="Handles user login, logout, and session management",
)

register_type(
    typ=EmailService,
    tags=[ProjectTags.SERVICE, ProjectTags.API],
    instructions="Handles sending various types of emails to users",
)


# Demo function to show agent in action
def demo_simple_mode():
    """Demo: Simple single-shot search mode (default)."""
    from ontonaut import CodebaseAgent

    print("\n" + "=" * 70)
    print("DEMO 1: Simple Mode (Single Search)")
    print("=" * 70)

    agent = CodebaseAgent(ai_client=client, iterative=False)

    print("\n📝 Query: 'How do I authenticate a user?'\n")
    agent.ask("How do I authenticate a user?")

    print("\n✅ Context found:")
    print(agent.context[:200] + "..." if len(agent.context) > 200 else agent.context)

    print("\n💡 AI Response:")
    print(agent.response[:500] + "..." if len(agent.response) > 500 else agent.response)


def demo_iterative_mode():
    """Demo: Iterative agent with planning and multiple searches."""
    from ontonaut import CodebaseAgent

    print("\n" + "=" * 70)
    print("DEMO 2: Iterative Mode (Intelligent Agent)")
    print("=" * 70)

    agent = CodebaseAgent(
        ai_client=client,
        iterative=True,  # 🔥 Enable intelligent agent
        max_iterations=3,  # Allow up to 3 search iterations
    )

    print("\n📝 Query: 'How do I authenticate a user and send them a welcome email?'\n")
    agent.ask("How do I authenticate a user and send them a welcome email?")

    print("\n🤔 Agent Thinking Process:")
    print(agent.context[:1000] + "..." if len(agent.context) > 1000 else agent.context)

    print("\n💡 Final Answer:")
    print(agent.response[:500] + "..." if len(agent.response) > 500 else agent.response)


def demo_direct_iterative_agent():
    """Demo: Using IterativeCodebaseAgent directly for full control."""
    from ontonaut import IterativeCodebaseAgent

    print("\n" + "=" * 70)
    print("DEMO 3: Direct IterativeCodebaseAgent Usage")
    print("=" * 70)

    agent = IterativeCodebaseAgent(ai_client=client, max_iterations=3, verbose=True)

    query = "Show me all authentication-related types and their methods"

    print(f"\n📝 Query: '{query}'\n")
    print("-" * 70)

    for update in agent.solve(query):
        update_type = update["type"]
        content = update["content"]
        iteration = update.get("iteration", 0)

        if update_type == "iteration_start":
            print(f"\n🔄 {content}")
            print("-" * 70)

        elif update_type == "thinking":
            print(f"\n💭 Thinking:")
            print(f"   {content[:200]}...")

        elif update_type == "action":
            print(f"\n🔧 Action: {content}")

        elif update_type == "observation":
            print(f"\n👁️  Observation:")
            print(f"   {content[:200]}...")

        elif update_type == "final_answer":
            print(f"\n✅ Final Answer:")
            print(f"   {content[:500]}...")
            print("-" * 70)


def interactive_mode():
    """Interactive mode: Ask your own questions."""
    from ontonaut import CodebaseAgent

    print("\n" + "=" * 70)
    print("INTERACTIVE MODE")
    print("=" * 70)

    print("\nAvailable modes:")
    print("  1. Simple (single search)")
    print("  2. Iterative (intelligent agent)")

    mode = input("\nChoose mode (1 or 2): ").strip()
    iterative = mode == "2"

    agent = CodebaseAgent(
        ai_client=client, iterative=iterative, max_iterations=5 if iterative else 1
    )

    print("\nType 'quit' to exit")
    print("-" * 70)

    while True:
        query = input("\n❓ Your question: ").strip()

        if query.lower() in ("quit", "exit", "q"):
            print("\n👋 Goodbye!")
            break

        if not query:
            continue

        print(f"\n{'🤔 Agent thinking...' if iterative else '🔍 Searching...'}\n")

        agent.ask(query)

        if iterative and agent.context:
            print("Agent Process:")
            print(agent.context[:500] + "..." if len(agent.context) > 500 else agent.context)

        print("\n💡 Answer:")
        print(agent.response[:800] + "..." if len(agent.response) > 800 else agent.response)
        print("-" * 70)


def main():
    """Run all demos."""
    print("\n🚀 Ontonaut Iterative Agent Demo")
    print("=" * 70)

    print("\nThis demo shows the iterative agent in action.")
    print("The agent can plan, search, and synthesize information")
    print("to answer complex questions about your codebase.")

    print("\nAvailable demos:")
    print("  1. Simple mode (default behavior)")
    print("  2. Iterative mode (intelligent agent)")
    print("  3. Direct IterativeCodebaseAgent usage")
    print("  4. Interactive mode (ask your own questions)")
    print("  5. Run all demos")

    choice = input("\nChoose demo (1-5): ").strip()

    if choice == "1":
        demo_simple_mode()
    elif choice == "2":
        demo_iterative_mode()
    elif choice == "3":
        demo_direct_iterative_agent()
    elif choice == "4":
        interactive_mode()
    elif choice == "5":
        demo_simple_mode()
        demo_iterative_mode()
        demo_direct_iterative_agent()
    else:
        print("Invalid choice. Running all demos...")
        demo_simple_mode()
        demo_iterative_mode()
        demo_direct_iterative_agent()

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()

