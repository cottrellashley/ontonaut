"""
Codebase Agent Widget

An AI-powered agent that searches your indexed codebase and answers questions
with relevant code snippets and explanations.
"""

from collections.abc import Iterator
from typing import Any

import anywidget
import traitlets

from ontonaut.indexing import RegisteredType
from ontonaut.iterative_agent import IterativeCodebaseAgent


class CodebaseAgent(anywidget.AnyWidget):
    """
    AI agent for codebase search and question answering.

    This widget integrates with the ontonaut indexing system to provide
    intelligent code search and documentation. Pass your own AI client
    for company-specific integrations.

    Example:
        ```python
        from ontonaut import CodebaseAgent
        import openai

        # With OpenAI
        agent = CodebaseAgent(ai_client=openai.OpenAI(api_key="..."))

        # With custom client
        agent = CodebaseAgent(ai_client=my_company_ai_wrapper)

        # Ask questions
        agent
        ```
    """

    _esm = """
    export function render({ model, el }) {
      const container = document.createElement("div");
      container.className = "codebase-agent-container";

      // Input section
      const inputSection = document.createElement("div");
      inputSection.className = "agent-input-section";

      const input = document.createElement("input");
      input.type = "text";
      input.className = "agent-input";
      input.placeholder = model.get("placeholder");
      input.value = model.get("query");

      const askButton = document.createElement("button");
      askButton.className = "agent-ask-button";
      askButton.textContent = "🔍 Search Codebase";

      let isProcessing = false;

      askButton.onclick = () => {
        if (isProcessing) return;  // Prevent double-click

        const query = input.value.trim();
        if (!query) return;

        isProcessing = true;
        askButton.disabled = true;
        askButton.textContent = "⏳ Searching...";

        model.send({ type: "ask", query: query });

        // Reset button after a delay (will be reset properly when response completes)
        setTimeout(() => {
          isProcessing = false;
          askButton.disabled = false;
          askButton.textContent = "🔍 Search Codebase";
        }, 1000);
      };

      inputSection.appendChild(input);
      inputSection.appendChild(askButton);

      // Context section (shows indexed types found)
      const contextSection = document.createElement("div");
      contextSection.className = "agent-context-section";
      contextSection.style.display = "none";

      const contextLabel = document.createElement("div");
      contextLabel.className = "agent-section-label";
      contextLabel.textContent = "📚 Indexed Types Found";

      const contextContent = document.createElement("div");
      contextContent.className = "agent-context-content";

      contextSection.appendChild(contextLabel);
      contextSection.appendChild(contextContent);

      // Response section
      const responseSection = document.createElement("div");
      responseSection.className = "agent-response-section";
      responseSection.style.display = "none";

      const responseLabel = document.createElement("div");
      responseLabel.className = "agent-section-label";
      responseLabel.textContent = "💡 AI Response";

      const responseContent = document.createElement("div");
      responseContent.className = "agent-response-content";

      responseSection.appendChild(responseLabel);
      responseSection.appendChild(responseContent);

      // Assemble
      container.appendChild(inputSection);
      container.appendChild(contextSection);
      container.appendChild(responseSection);
      el.appendChild(container);

      // Handle input changes
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          askButton.click();
        }
      });

      // Listen for context updates
      model.on("change:context", () => {
        const context = model.get("context");
        if (context) {
          contextContent.innerHTML = context;
          contextSection.style.display = "block";
        } else {
          contextSection.style.display = "none";
        }
      });

      // Listen for response updates (streaming)
      model.on("change:response", () => {
        const response = model.get("response");
        if (response) {
          responseContent.innerHTML = response;
          responseSection.style.display = "block";
        }
      });

      // Listen for error updates
      model.on("change:error", () => {
        const error = model.get("error");
        if (error) {
          responseContent.innerHTML = `<div class="agent-error">${error}</div>`;
          responseSection.style.display = "block";
        }
      });
    }

    export default { render };
    """

    _css = """
    .codebase-agent-container {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      border: 1px solid #e8eaed;
      border-radius: 8px;
      background: white;
      padding: 16px;
      margin: 12px 0;
    }

    .agent-input-section {
      display: flex;
      gap: 12px;
      margin-bottom: 16px;
    }

    .agent-input {
      flex: 1;
      padding: 10px 14px;
      font-size: 14px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      outline: none;
      transition: border-color 0.2s;
    }

    .agent-input:focus {
      border-color: #10b981;
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
    }

    .agent-ask-button {
      padding: 10px 20px;
      font-size: 14px;
      font-weight: 600;
      background: #10b981;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .agent-ask-button:hover {
      background: #059669;
      transform: translateY(-1px);
    }

    .agent-ask-button:active {
      transform: translateY(0);
    }

    .agent-section-label {
      font-size: 12px;
      font-weight: 700;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e8eaed;
    }

    .agent-context-section,
    .agent-response-section {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid #e8eaed;
    }

    .agent-context-content {
      font-size: 13px;
      line-height: 1.6;
    }

    .agent-context-item {
      background: #f9fafb;
      border-left: 3px solid #10b981;
      padding: 12px;
      margin-bottom: 12px;
      border-radius: 4px;
    }

    .agent-context-item-name {
      font-weight: 600;
      color: #10b981;
      margin-bottom: 4px;
    }

    .agent-context-item-path {
      font-size: 11px;
      color: #6b7280;
      font-family: monospace;
      margin-bottom: 8px;
    }

    .agent-context-item-doc {
      color: #374151;
      margin-bottom: 8px;
    }

    .agent-context-item-tags {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .agent-context-tag {
      background: #e8eaed;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 11px;
      color: #4b5563;
    }

    .agent-response-content {
      font-size: 14px;
      line-height: 1.7;
      color: #1f2937;
    }

    .agent-response-content h1,
    .agent-response-content h2,
    .agent-response-content h3 {
      margin-top: 16px;
      margin-bottom: 8px;
      color: #111827;
    }

    .agent-response-content code {
      background: #f3f4f6;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: "SF Mono", Monaco, monospace;
      font-size: 13px;
      color: #d73a49;
    }

    .agent-response-content pre {
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 16px;
      border-radius: 6px;
      overflow-x: auto;
      margin: 12px 0;
    }

    .agent-response-content pre code {
      background: none;
      color: inherit;
      padding: 0;
    }

    .agent-error {
      color: #dc2626;
      background: #fef2f2;
      padding: 12px;
      border-left: 3px solid #dc2626;
      border-radius: 4px;
    }

    /* Iterative Agent Styles */
    .agent-iteration {
      font-weight: 600;
      color: #10b981;
      margin: 16px 0 8px 0;
      padding: 8px;
      background: #f0fdf4;
      border-left: 3px solid #10b981;
      border-radius: 4px;
    }

    .agent-thinking {
      background: #f3f4f6;
      padding: 12px;
      margin: 8px 0;
      border-left: 3px solid #6b7280;
      border-radius: 4px;
      font-size: 13px;
      white-space: pre-wrap;
    }

    .agent-action {
      background: #dbeafe;
      padding: 12px;
      margin: 8px 0;
      border-left: 3px solid #3b82f6;
      border-radius: 4px;
      font-size: 13px;
    }

    .agent-observation {
      background: #fef3c7;
      padding: 12px;
      margin: 8px 0;
      border-left: 3px solid #f59e0b;
      border-radius: 4px;
      font-size: 12px;
    }

    .agent-observation pre {
      background: #fffbeb;
      padding: 8px;
      border-radius: 3px;
      overflow-x: auto;
      margin: 8px 0 0 0;
      font-size: 11px;
    }
    """

    # Traitlets
    query = traitlets.Unicode("").tag(sync=True)
    placeholder = traitlets.Unicode("Ask about your codebase...").tag(sync=True)
    context = traitlets.Unicode("").tag(sync=True)
    response = traitlets.Unicode("").tag(sync=True)
    error = traitlets.Unicode("").tag(sync=True)
    theme = traitlets.Unicode("light").tag(sync=True)

    def __init__(
        self,
        ai_client: Any = None,
        query: str = "",
        placeholder: str = "Ask about your codebase...",
        theme: str = "light",
        iterative: bool = False,
        max_iterations: int = 5,
        **kwargs: Any,
    ) -> None:
        """
        Initialize codebase agent.

        Args:
            ai_client: AI client instance (OpenAI, Anthropic, or custom wrapper)
            query: Initial query
            placeholder: Placeholder text for input
            theme: UI theme ("light" or "dark")
            iterative: Whether to use iterative agent mode (default: True)
            max_iterations: Maximum iterations for iterative mode (default: 5)
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.ai_client = ai_client
        self.query = query
        self.placeholder = placeholder
        self.theme = theme
        self.iterative = iterative
        self.max_iterations = max_iterations
        self._is_processing = False  # Flag to prevent concurrent processing

        # Register message handler
        self.on_msg(self._handle_message)

    def _handle_message(self, widget: Any, content: dict, buffers: list) -> None:
        """Handle messages from frontend."""
        msg_type = content.get("type")

        if msg_type == "ask":
            # Prevent concurrent processing
            if self._is_processing:
                return

            query = content.get("query", "")
            if query:
                # Set flag BEFORE processing to prevent race conditions
                self._is_processing = True
                try:
                    self._process_question(query)
                finally:
                    # Always clear processing flag
                    self._is_processing = False

    def _search_codebase(self, query: str) -> list[RegisteredType]:
        """
        Search indexed codebase using AI-extracted keywords.

        Uses the AI to intelligently extract search terms from the natural language query,
        then searches the codebase for matching types, methods, and properties.

        Args:
            query: User's search query (natural language)

        Returns:
            List of relevant RegisteredType instances, ranked by relevance
        """
        from ontonaut.indexing import get_registry

        # Use AI to extract keywords
        keywords = self._extract_keywords_with_ai(query)

        if not keywords:
            return []

        # Get all registered types
        registry = get_registry()
        all_types = registry.get_all()

        # Score each type based on keyword matches
        scored_results = []
        for typ in all_types:
            score = self._calculate_relevance_score(typ, keywords)
            if score > 0:
                scored_results.append((typ, score))

        # Sort by score (highest first) and return top 10
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return [typ for typ, score in scored_results[:10]]

    def _extract_keywords_with_ai(self, query: str) -> list[str]:
        """
        Use AI to extract search keywords from natural language query.

        Args:
            query: Natural language query

        Returns:
            List of extracted keywords
        """
        if not self.ai_client:
            # Fallback to simple extraction if no AI client
            import re

            STOP_WORDS = {
                "how",
                "do",
                "i",
                "can",
                "you",
                "what",
                "where",
                "when",
                "why",
                "is",
                "are",
                "the",
                "a",
                "an",
                "to",
                "for",
                "of",
                "in",
                "on",
                "with",
                "this",
                "that",
                "please",
                "show",
                "me",
                "find",
                "get",
                "use",
                "using",
                "does",
                "has",
                "have",
            }
            keywords = re.findall(r"\b\w+\b", query.lower())
            return [k for k in keywords if len(k) >= 3 and k not in STOP_WORDS]

        prompt = f"""Extract search keywords from this question for searching a Python codebase.
Return ONLY a comma-separated list of keywords. Include:
- Main concepts (e.g., "user", "authentication")
- Action words (e.g., "create", "validate", "authenticate")
- Related terms and synonyms
- Technical terms

Question: "{query}"

Keywords:"""

        try:
            # Try OpenAI-style client
            if hasattr(self.ai_client, "chat") and hasattr(
                self.ai_client.chat, "completions"
            ):
                response = self.ai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=100,
                )
                keywords_text = response.choices[0].message.content.strip()
            # Try callable client
            elif callable(self.ai_client):
                keywords_text = self.ai_client(prompt)
                if hasattr(keywords_text, "__iter__") and not isinstance(
                    keywords_text, str
                ):
                    # If it's a generator/iterator, consume it
                    keywords_text = "".join(keywords_text)
            else:
                # Fallback
                import re

                keywords = re.findall(r"\b\w+\b", query.lower())
                return [k for k in keywords if len(k) >= 3]

            # Parse comma-separated keywords
            keywords = [k.strip().lower() for k in keywords_text.split(",")]
            keywords = [k for k in keywords if k and len(k) >= 2]
            return keywords[:15]  # Limit to 15 keywords

        except Exception:
            # Fallback to simple extraction on any error
            import re

            STOP_WORDS = {
                "how",
                "do",
                "i",
                "can",
                "you",
                "what",
                "where",
                "when",
                "why",
                "is",
                "are",
                "the",
                "a",
                "an",
                "to",
                "for",
                "of",
                "in",
                "on",
                "with",
                "this",
                "that",
                "please",
                "show",
                "me",
                "find",
                "get",
                "use",
                "using",
                "does",
                "has",
                "have",
            }
            keywords = re.findall(r"\b\w+\b", query.lower())
            return [k for k in keywords if len(k) >= 3 and k not in STOP_WORDS]

    def _calculate_relevance_score(
        self, typ: RegisteredType, keywords: list[str]
    ) -> int:
        """
        Calculate relevance score for a type based on keywords.

        Scoring weights:
        - Type name exact match: 100 points
        - Type name partial match: 50 points
        - Method name match: 40 points
        - Property name match: 35 points
        - Instructions match: 30 points
        - Docstring match: 20 points
        - Method docstring match: 15 points
        - Tag match: 10 points

        Args:
            typ: RegisteredType to score
            keywords: List of search keywords

        Returns:
            Relevance score (higher is better)
        """
        score = 0
        typ_name_lower = typ.name.lower()
        docstring_lower = typ.docstring.lower()
        instructions_lower = typ.instructions.lower()
        module_lower = typ.module.lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Type name matches (highest priority)
            if typ_name_lower == keyword_lower:
                score += 100
            elif keyword_lower in typ_name_lower:
                score += 50

            # Module matches
            if keyword_lower in module_lower:
                score += 25

            # Method name matches
            for method_name, method_info in typ.methods.items():
                if keyword_lower in method_name.lower():
                    score += 40
                # Method docstring matches
                if (
                    method_info.get("docstring")
                    and keyword_lower in method_info["docstring"].lower()
                ):
                    score += 15

            # Property name matches
            for prop_name, prop_info in typ.properties.items():
                if keyword_lower in prop_name.lower():
                    score += 35
                # Property docstring matches
                if (
                    prop_info.get("docstring")
                    and keyword_lower in prop_info["docstring"].lower()
                ):
                    score += 10

            # Instructions match
            if keyword_lower in instructions_lower:
                score += 30

            # Docstring match
            if keyword_lower in docstring_lower:
                score += 20

            # Tag match
            for tag in typ.tags:
                if keyword_lower in str(tag).lower():
                    score += 10

        return score

    def _build_context_html(self, types: list[RegisteredType]) -> str:
        """
        Build HTML representation of context types.

        Args:
            types: List of RegisteredType instances

        Returns:
            HTML string
        """
        if not types:
            return "<p style='color: #6b7280;'>No indexed types found. Register types with @index_type decorator.</p>"

        html_parts = []
        for t in types:
            tags_html = "".join(
                f'<span class="agent-context-tag">{tag}</span>' for tag in t.tags
            )

            html_parts.append(
                f"""
                <div class="agent-context-item">
                    <div class="agent-context-item-name">{t.name}</div>
                    <div class="agent-context-item-path">{t.cls_path}</div>
                    <div class="agent-context-item-doc">{t.docstring[:200]}...</div>
                    <div class="agent-context-item-tags">{tags_html}</div>
                </div>
            """
            )

        return "".join(html_parts)

    def _build_context_for_ai(self, types: list[RegisteredType]) -> str:
        """
        Build context string for AI.

        Args:
            types: List of RegisteredType instances

        Returns:
            Context string for AI prompt
        """
        if not types:
            return "No relevant code found in the indexed codebase."

        context_parts = [
            "# Relevant Code from Indexed Codebase\n",
            "The following types and their methods are relevant to your question:\n\n",
        ]

        for t in types:
            context_parts.append(f"## {t.cls_path}\n")
            context_parts.append(f"**Tags:** {', '.join(str(tag) for tag in t.tags)}\n")
            context_parts.append(f"**Description:** {t.docstring}\n")

            if t.instructions:
                context_parts.append(f"**Notes:** {t.instructions}\n")

            context_parts.append("\n### Methods:\n")
            for method_name, method_info in list(t.methods.items())[
                :5
            ]:  # Limit methods
                sig = method_info["signature"] or "()"
                context_parts.append(f"- `{method_name}{sig}`")
                if method_info["docstring"]:
                    context_parts.append(f": {method_info['docstring'][:100]}")
                context_parts.append("\n")

            if t.properties:
                context_parts.append("\n### Properties:\n")
                for prop_name, prop_info in list(t.properties.items())[:3]:
                    context_parts.append(
                        f"- `{prop_name}`: {prop_info['docstring'][:80]}\n"
                    )

            context_parts.append("\n")

        return "".join(context_parts)

    def _stream_ai_response(self, query: str, context: str) -> Iterator[str]:
        """
        Stream AI response.

        Args:
            query: User query
            context: Codebase context

        Yields:
            Response chunks
        """
        if self.ai_client is None:
            yield "❌ No AI client provided. Pass an AI client to CodebaseAgent(ai_client=...)."
            return

        system_prompt = f"""You are a helpful AI assistant that answers questions about a Python codebase.
You have access to indexed code with docstrings, method signatures, and metadata.

Use the provided context to answer the user's question with:
1. Clear explanations
2. Relevant code examples
3. Best practices

Context:
{context}

Answer the question directly and concisely. Include code snippets when helpful.
Use markdown formatting for code blocks."""

        try:
            # Try OpenAI-style client first
            if hasattr(self.ai_client, "chat") and hasattr(
                self.ai_client.chat, "completions"
            ):
                response = self.ai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query},
                    ],
                    stream=True,
                    temperature=0.7,
                )

                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            # Try callable client (custom wrapper)
            elif callable(self.ai_client):
                result = self.ai_client(query, context=context)

                # Handle generator
                if hasattr(result, "__iter__") and not isinstance(result, str):
                    yield from result
                else:
                    yield str(result)

            else:
                yield "❌ Unsupported AI client type. Client should have .chat.completions or be callable."

        except Exception as e:
            yield f"❌ Error calling AI client: {str(e)}"

    def _process_question(self, query: str) -> None:
        """
        Process user question and generate response.

        Args:
            query: User question
        """
        try:
            # Clear previous state
            self.error = ""
            self.response = ""
            self.context = ""

            if self.iterative:
                # Use iterative agent mode
                self._process_with_iterative_agent(query)
            else:
                # Use simple single-shot mode
                self._process_with_simple_search(query)

        except Exception as e:
            self.error = f"Error processing question: {str(e)}"

    def _process_with_simple_search(self, query: str) -> None:
        """Process question with simple single-shot search (original behavior)."""
        # Search codebase
        relevant_types = self._search_codebase(query)

        # Build and display context
        self.context = self._build_context_html(relevant_types)

        # Build context for AI
        ai_context = self._build_context_for_ai(relevant_types)

        # Stream AI response
        response_parts = []
        for chunk in self._stream_ai_response(query, ai_context):
            response_parts.append(chunk)
            # Convert markdown to HTML for display
            self.response = self._markdown_to_html("".join(response_parts))

    def _process_with_iterative_agent(self, query: str) -> None:
        """Process question with iterative agent that can search multiple times."""
        if not self.ai_client:
            self.error = "❌ No AI client provided. Cannot use iterative mode."
            return

        # Create iterative agent
        agent = IterativeCodebaseAgent(
            ai_client=self.ai_client,
            max_iterations=self.max_iterations,
            verbose=True,
        )

        # Track all actions for context display
        actions_log = []
        response_parts = []

        # Run agent loop
        for update in agent.solve(query):
            update_type = update["type"]
            content = update["content"]
            update.get("iteration", 0)

            if update_type == "iteration_start":
                # Show iteration number
                actions_log.append(f"<div class='agent-iteration'>🔄 {content}</div>")

            elif update_type == "thinking":
                # Show agent's reasoning
                actions_log.append(
                    f"<div class='agent-thinking'><strong>💭 Thinking:</strong><br>{self._escape_html(content)}</div>"
                )

            elif update_type == "action":
                # Show tool usage
                actions_log.append(
                    f"<div class='agent-action'><strong>🔧 Action:</strong> {self._escape_html(content)}</div>"
                )

            elif update_type == "observation":
                # Show tool results (truncated for display)
                truncated = content[:500] + "..." if len(content) > 500 else content
                actions_log.append(
                    f"<div class='agent-observation'><strong>👁️ Observation:</strong><pre>{self._escape_html(truncated)}</pre></div>"
                )

            elif update_type == "final_answer":
                # Show final answer
                response_parts.append(content)

            # Update context with actions log
            self.context = "".join(actions_log)

            # Update response with final answer
            if response_parts:
                self.response = self._markdown_to_html("".join(response_parts))

    def _markdown_to_html(self, markdown: str) -> str:
        """
        Simple markdown to HTML conversion.

        Args:
            markdown: Markdown text

        Returns:
            HTML string
        """
        import re

        html = markdown

        # Code blocks
        html = re.sub(
            r"```(\w+)?\n(.*?)```",
            r'<pre><code class="language-\1">\2</code></pre>',
            html,
            flags=re.DOTALL,
        )

        # Inline code
        html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

        # Headers
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Line breaks
        html = html.replace("\n", "<br>")

        return html

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def ask(self, query: str) -> None:
        """
        Ask a question about the codebase programmatically.

        Args:
            query: Question to ask
        """
        # Prevent concurrent processing
        if self._is_processing:
            return

        self.query = query
        self._is_processing = True
        try:
            self._process_question(query)
        finally:
            self._is_processing = False
