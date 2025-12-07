"""Tests for CodebaseAgent widget."""

import pytest
from ontonaut import CodebaseAgent, IndexTag, clear_registry, index_type


# Test fixtures
class TestTags(IndexTag):
    """Test tags."""

    DATABASE = "database"
    API = "api"


@pytest.fixture(autouse=True)
def clean_registry():
    """Clear registry before and after each test."""
    clear_registry()
    yield
    clear_registry()


@pytest.fixture
def sample_types():
    """Register sample types for testing."""

    @index_type(tags=[TestTags.DATABASE], instructions="User model")
    class User:
        """User authentication model."""

        def authenticate(self, password: str) -> bool:
            """Verify password."""
            return True

        @property
        def is_active(self) -> bool:
            """Check if active."""
            return True

    @index_type(tags=[TestTags.API], instructions="User service")
    class UserService:
        """Service for user operations."""

        def create_user(self, username: str) -> dict:
            """Create user."""
            return {"id": 1}

    return [User, UserService]


class MockAIClient:
    """Mock AI client for testing."""

    class Chat:
        def __init__(self, parent):
            self.parent = parent
            self.completions = MockAIClient.Completions(parent)

    class Completions:
        def __init__(self, parent):
            self.parent = parent

        def create(self, **kwargs):
            self.parent.called_with = kwargs
            # Return mock streaming response
            return MockAIClient.StreamResponse(self.parent.response_text)

    class StreamResponse:
        def __init__(self, text):
            self.text = text
            self.index = 0

        def __iter__(self):
            for char in self.text:
                yield MockAIClient.StreamChunk(char)

    class StreamChunk:
        def __init__(self, char):
            self.choices = [MockAIClient.Choice(char)]

    class Choice:
        def __init__(self, char):
            self.delta = MockAIClient.Delta(char)

    class Delta:
        def __init__(self, char):
            self.content = char

    def __init__(self, response_text="Mock response"):
        self.response_text = response_text
        self.called_with = None
        self.chat = MockAIClient.Chat(self)


class TestCodebaseAgent:
    """Test CodebaseAgent widget."""

    def test_initialization(self):
        """Test agent initialization."""
        mock_client = MockAIClient()
        agent = CodebaseAgent(ai_client=mock_client)

        assert agent.ai_client is mock_client
        assert agent.query == ""
        assert agent.placeholder == "Ask about your codebase..."
        assert agent.theme == "light"

    def test_initialization_with_params(self):
        """Test initialization with custom parameters."""
        agent = CodebaseAgent(
            ai_client=None,
            query="test query",
            placeholder="Custom placeholder",
            theme="dark",
        )

        assert agent.query == "test query"
        assert agent.placeholder == "Custom placeholder"
        assert agent.theme == "dark"

    def test_search_codebase(self, sample_types):
        """Test codebase search functionality."""
        agent = CodebaseAgent()
        results = agent._search_codebase("user")

        assert len(results) > 0
        assert any(r.name == "User" for r in results)

    def test_search_codebase_no_results(self):
        """Test search with no results."""
        agent = CodebaseAgent()
        results = agent._search_codebase("nonexistent")

        assert len(results) == 0

    def test_build_context_html(self, sample_types):
        """Test building HTML context."""
        agent = CodebaseAgent()
        results = agent._search_codebase("user")
        html = agent._build_context_html(results)

        assert "User" in html
        assert "agent-context-item" in html
        assert "User authentication model" in html

    def test_build_context_html_empty(self):
        """Test building HTML with no types."""
        agent = CodebaseAgent()
        html = agent._build_context_html([])

        assert "No indexed types found" in html

    def test_build_context_for_ai(self, sample_types):
        """Test building AI context."""
        agent = CodebaseAgent()
        results = agent._search_codebase("user")
        context = agent._build_context_for_ai(results)

        assert "User" in context
        assert "authenticate" in context
        assert "User authentication model" in context
        assert "Methods:" in context

    def test_build_context_for_ai_empty(self):
        """Test AI context with no types."""
        agent = CodebaseAgent()
        context = agent._build_context_for_ai([])

        assert "No relevant code found" in context

    def test_stream_ai_response_no_client(self):
        """Test streaming without AI client."""
        agent = CodebaseAgent()  # No client
        chunks = list(agent._stream_ai_response("test", "context"))

        assert len(chunks) > 0
        assert "No AI client provided" in chunks[0]

    def test_stream_ai_response_with_mock_client(self, sample_types):
        """Test streaming with mock OpenAI-style client."""
        mock_client = MockAIClient("Test response from AI")
        agent = CodebaseAgent(ai_client=mock_client)

        chunks = list(agent._stream_ai_response("test question", "test context"))
        response = "".join(chunks)

        assert "Test response from AI" == response
        assert mock_client.called_with is not None
        assert "test question" in str(mock_client.called_with)

    def test_stream_ai_response_with_callable(self):
        """Test streaming with callable client."""

        def mock_callable(query, context=None):
            return f"Response to: {query}"

        agent = CodebaseAgent(ai_client=mock_callable)
        chunks = list(agent._stream_ai_response("test", "context"))
        response = "".join(chunks)

        assert "Response to: test" == response

    def test_stream_ai_response_with_generator_callable(self):
        """Test streaming with generator callable."""

        def mock_generator(query, context=None):
            for word in f"Response to {query}".split():
                yield word + " "

        agent = CodebaseAgent(ai_client=mock_generator)
        chunks = list(agent._stream_ai_response("test", "context"))
        response = "".join(chunks)

        assert "Response to test" in response

    def test_stream_ai_response_error_handling(self):
        """Test error handling in streaming."""

        class BrokenClient:
            class Chat:
                class Completions:
                    def create(self, **kwargs):
                        raise ValueError("Broken client")

                completions = None

                def __init__(self):
                    self.completions = BrokenClient.Chat.Completions()

            chat = None

            def __init__(self):
                self.chat = BrokenClient.Chat()

        agent = CodebaseAgent(ai_client=BrokenClient())
        chunks = list(agent._stream_ai_response("test", "context"))
        response = "".join(chunks)

        assert "Error calling AI client" in response
        assert "Broken client" in response

    def test_markdown_to_html(self):
        """Test markdown conversion."""
        agent = CodebaseAgent()

        # Test code blocks
        markdown = "```python\ndef hello():\n    pass\n```"
        html = agent._markdown_to_html(markdown)
        assert "<pre>" in html
        assert "<code" in html

        # Test inline code
        markdown = "Use `code` here"
        html = agent._markdown_to_html(markdown)
        assert "<code>code</code>" in html

        # Test headers
        markdown = "# Header 1\n## Header 2\n### Header 3"
        html = agent._markdown_to_html(markdown)
        assert "<h1>Header 1</h1>" in html
        assert "<h2>Header 2</h2>" in html
        assert "<h3>Header 3</h3>" in html

    def test_ask_method(self):
        """Test programmatic ask method."""
        from ontonaut import get_registry

        # Register types inline
        @index_type(tags=[TestTags.DATABASE])
        class User:
            """User authentication model."""

            def authenticate(self, password: str) -> bool:
                """Verify password."""
                return True

        # Verify registration
        assert len(get_registry()) > 0, "Registry is empty after registration"

        mock_client = MockAIClient("AI response")
        agent = CodebaseAgent(ai_client=mock_client)

        agent.ask("How do I authenticate a user?")

        assert agent.query == "How do I authenticate a user?"
        assert len(agent.context) > 0
        assert "User" in agent.context

    def test_process_question_error_handling(self):
        """Test error handling in question processing."""

        class BrokenSearchAgent(CodebaseAgent):
            def _search_codebase(self, query):
                raise RuntimeError("Search failed")

        agent = BrokenSearchAgent()
        agent._process_question("test")

        assert "Error processing question" in agent.error
        assert "Search failed" in agent.error

    def test_search_limits_results(self, sample_types):
        """Test that search limits results to 10."""
        # Register many types
        for i in range(15):

            @index_type(tags=[TestTags.API], instructions=f"Service {i}")
            class DynamicService:
                """User service."""

                pass

        agent = CodebaseAgent()
        results = agent._search_codebase("user service")

        assert len(results) <= 10

    def test_context_includes_properties(self, sample_types):
        """Test that context includes properties."""
        agent = CodebaseAgent()
        results = agent._search_codebase("user")
        context = agent._build_context_for_ai(results)

        assert "Properties:" in context
        assert "is_active" in context

    def test_context_includes_tags(self, sample_types):
        """Test that context includes tags."""
        agent = CodebaseAgent()
        results = agent._search_codebase("user")
        context = agent._build_context_for_ai(results)

        assert "Tags:" in context
        assert "database" in context.lower() or "api" in context.lower()

    def test_unsupported_client_type(self):
        """Test with unsupported client type."""
        agent = CodebaseAgent(ai_client="not a valid client")
        chunks = list(agent._stream_ai_response("test", "context"))
        response = "".join(chunks)

        assert "Unsupported AI client type" in response


class TestCodebaseAgentIntegration:
    """Integration tests for CodebaseAgent."""

    def test_full_workflow(self):
        """Test complete workflow from question to response."""

        # Register types inline
        @index_type(tags=[TestTags.DATABASE])
        class User:
            """User authentication model."""

            def authenticate(self, password: str) -> bool:
                """Verify password."""
                return True

        mock_client = MockAIClient(
            "Here's how to authenticate:\n```python\nuser.authenticate(password)\n```"
        )
        agent = CodebaseAgent(ai_client=mock_client)

        # Ask question
        agent.ask("How do I authenticate a user?")

        # Check context was built
        assert len(agent.context) > 0
        assert "User" in agent.context

        # Check response was generated
        assert len(agent.response) > 0

        # Check no errors
        assert agent.error == ""

    def test_handles_empty_codebase(self):
        """Test behavior with empty codebase."""
        mock_client = MockAIClient("No relevant code found.")
        agent = CodebaseAgent(ai_client=mock_client)

        agent.ask("How do I do something?")

        assert "No indexed types found" in agent.context
        assert len(agent.response) > 0  # AI still responds


class TestCodebaseAgentSmartSearch:
    """Tests for smart search with keyword extraction and scoring."""

    def test_keyword_extraction_and_stop_words(self, sample_types):
        """Test that keywords are extracted and stop words are filtered."""
        agent = CodebaseAgent(ai_client=MockAIClient())

        # Query with many stop words
        results = agent._search_codebase("How do I authenticate the user?")

        # Should find User (has authenticate method)
        assert len(results) > 0
        assert any(r.name == "User" for r in results)

    def test_method_name_search(self, sample_types):
        """Test searching by method name."""
        agent = CodebaseAgent(ai_client=MockAIClient())

        # Search by method name
        results = agent._search_codebase("create user")

        # Should find UserService (has create_user method)
        assert len(results) > 0
        assert any(r.name == "UserService" for r in results)

    def test_property_name_search(self, sample_types):
        """Test searching by property name."""
        agent = CodebaseAgent(ai_client=MockAIClient())

        results = agent._search_codebase("is active")

        # Should find User (has is_active property)
        assert len(results) > 0
        assert any(r.name == "User" for r in results)

    def test_relevance_scoring(self):
        """Test that results are ranked by relevance."""
        from ontonaut import register_type

        # Register types with different relevance
        class AuthService:
            """Authentication service."""

            def authenticate(self, user: str) -> bool:
                """Authenticate user."""
                return True

        class User:
            """User model."""

            pass

        class EmailService:
            """Email service."""

            pass

        register_type(typ=AuthService, tags=[TestTags.API], instructions="Auth")
        register_type(typ=User, tags=[TestTags.DATABASE], instructions="User")
        register_type(typ=EmailService, tags=[TestTags.API], instructions="Email")

        agent = CodebaseAgent(ai_client=MockAIClient())
        results = agent._search_codebase("authenticate user")

        # User should rank highest (exact name match: 100 points)
        # AuthService should rank second (method match: 40 points)
        assert len(results) >= 2
        assert results[0].name == "User"  # Exact name match wins
        assert results[1].name == "AuthService"  # Has authenticate method

    def test_exact_name_match_scores_highest(self, sample_types):
        """Test that exact type name matches score highest."""
        agent = CodebaseAgent(ai_client=MockAIClient())

        results = agent._search_codebase("User")

        # Both User and UserService should be in results (both contain "user")
        assert len(results) > 0
        result_names = [r.name for r in results]
        assert "User" in result_names
        assert "UserService" in result_names

    def test_empty_query_returns_empty_results(self):
        """Test that queries with only stop words return empty."""
        agent = CodebaseAgent(ai_client=MockAIClient())

        results = agent._search_codebase("how do I the")

        assert len(results) == 0

    def test_tag_search(self, sample_types):
        """Test searching by tag names."""
        agent = CodebaseAgent(ai_client=MockAIClient())

        results = agent._search_codebase("database")

        # Should find User (tagged with DATABASE)
        assert len(results) > 0
        assert any(r.name == "User" for r in results)

    def test_calculate_relevance_score(self, sample_types):
        """Test relevance score calculation."""
        from ontonaut import get_registry

        agent = CodebaseAgent(ai_client=MockAIClient())
        registry = get_registry()
        user_type = registry.get("sample_types.User")

        if not user_type:
            # Try to get it by searching
            all_types = registry.get_all()
            user_type = next((t for t in all_types if t.name == "User"), None)

        assert user_type is not None

        # Score with relevant keyword
        score = agent._calculate_relevance_score(user_type, ["authenticate"])
        assert score > 0  # Should have positive score (method match)

        # Score with irrelevant keyword
        score_low = agent._calculate_relevance_score(user_type, ["xyz123"])
        assert score_low == 0  # Should have zero score
