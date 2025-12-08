"""
Iterative Agent for Codebase Exploration.

Implements a ReAct-style agent loop where the agent can:
1. Think about what information it needs
2. Act by using tools to search the codebase
3. Observe the results
4. Repeat until it has enough information to answer
"""

import json
from collections.abc import Iterator
from typing import Any

from ontonaut.agent_tools import AgentTools


class IterativeCodebaseAgent:
    """
    An iterative agent that can plan, search, and synthesize information
    from an indexed codebase using multiple search iterations.
    """

    def __init__(
        self,
        ai_client: Any,
        max_iterations: int = 5,
        verbose: bool = True,
    ):
        """
        Initialize the iterative agent.

        Args:
            ai_client: AI client for generating responses (OpenAI-compatible)
            max_iterations: Maximum number of search iterations
            verbose: Whether to stream thinking process
        """
        self.ai_client = ai_client
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.tools = AgentTools()

    def solve(self, query: str) -> Iterator[dict[str, Any]]:
        """
        Solve a user query through iterative exploration of the codebase.

        Yields status updates as the agent thinks, acts, and observes.

        Args:
            query: User's question about the codebase

        Yields:
            Dictionary with status updates:
            - type: 'thinking', 'action', 'observation', 'answer'
            - content: The content of the update
            - iteration: Current iteration number
        """
        # Initial system prompt
        system_prompt = self._build_system_prompt()

        # Track conversation history
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {query}"}
        ]

        # Agent loop
        for iteration in range(self.max_iterations):
            yield {
                "type": "iteration_start",
                "content": f"Iteration {iteration + 1}/{self.max_iterations}",
                "iteration": iteration + 1,
            }

            # Think: Agent decides what to do next
            thinking_response = self._get_ai_response(messages, mode="thinking")

            yield {
                "type": "thinking",
                "content": thinking_response,
                "iteration": iteration + 1,
            }

            # Parse the thinking response to extract action
            action = self._parse_action(thinking_response)

            if action["type"] == "answer":
                # Agent has enough information, provide final answer
                yield {
                    "type": "final_answer",
                    "content": action["content"],
                    "iteration": iteration + 1,
                }
                break

            elif action["type"] == "tool":
                # Agent wants to use a tool
                yield {
                    "type": "action",
                    "content": f"Using tool: {action['tool_name']} with args: {action['args']}",
                    "iteration": iteration + 1,
                }

                # Execute the tool
                observation = self._execute_tool(action["tool_name"], action["args"])

                yield {
                    "type": "observation",
                    "content": json.dumps(observation, indent=2),
                    "iteration": iteration + 1,
                }

                # Add to conversation history
                messages.append({
                    "role": "assistant",
                    "content": f"THINKING: {thinking_response}\n\nACTION: {action['tool_name']}({action['args']})"
                })
                messages.append({
                    "role": "user",
                    "content": f"OBSERVATION: {json.dumps(observation)}"
                })

        # If we hit max iterations without answering, force a final answer
        if iteration == self.max_iterations - 1:
            yield {
                "type": "thinking",
                "content": "Maximum iterations reached. Synthesizing final answer from gathered information.",
                "iteration": self.max_iterations,
            }

            messages.append({
                "role": "user",
                "content": "Please provide a final answer based on all the information gathered."
            })

            final_answer = self._get_ai_response(messages, mode="answer")

            yield {
                "type": "final_answer",
                "content": final_answer,
                "iteration": self.max_iterations,
            }

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']} (args: {tool['args']})"
            for tool in self.tools.get_available_tools()
        ])

        return f"""You are an intelligent codebase exploration agent. Your job is to answer questions about a Python codebase by iteratively searching and exploring it.

You have access to the following tools:

{tools_desc}

When answering a question, follow this process:

1. THINK about what information you need
2. Decide which tool to use and what arguments to pass
3. Observe the results
4. Determine if you need more information or can answer

Your response should follow this format:

THINKING: [Your reasoning about what to do next]

ACTION: [One of the following]
- TOOL: tool_name(arg1="value1", arg2="value2")
- ANSWER: [Your final answer when you have enough information]

Important guidelines:
- Start with broad searches, then narrow down
- Use search_types first to find relevant types
- Use get_type_details to get full information about specific types
- Search iteratively - you may need multiple searches
- When you have enough information, provide a clear, well-structured answer with code examples
- Be thorough but efficient - don't waste iterations

Always format your response as:
THINKING: [your thoughts]
ACTION: TOOL: tool_name(args) OR ANSWER: [final answer]
"""

    def _get_ai_response(self, messages: list[dict], mode: str = "thinking") -> str:
        """
        Get response from AI client.

        Args:
            messages: Conversation history
            mode: 'thinking' or 'answer'

        Returns:
            AI response text
        """
        try:
            if hasattr(self.ai_client, "chat") and hasattr(self.ai_client.chat, "completions"):
                # OpenAI-style client
                response = self.ai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.3 if mode == "thinking" else 0.7,
                    max_tokens=1000 if mode == "thinking" else 2000,
                )
                return response.choices[0].message.content  # type: ignore[no-any-return]
            elif callable(self.ai_client):
                # Custom callable client
                response = self.ai_client(messages[-1]["content"])
                if hasattr(response, "__iter__") and not isinstance(response, str):
                    return "".join(response)
                return str(response)
            else:
                return "Error: Unsupported AI client type"
        except Exception as e:
            return f"Error calling AI client: {str(e)}"

    def _parse_action(self, response: str) -> dict[str, Any]:
        """
        Parse the agent's response to extract the action.

        Args:
            response: Agent's text response

        Returns:
            Dictionary describing the action
        """
        # Look for ACTION: line
        lines = response.split("\n")
        action_line = None

        for line in lines:
            if line.strip().startswith("ACTION:"):
                action_line = line.strip()[7:].strip()
                break

        if not action_line:
            # No explicit action, assume we need more thinking
            return {"type": "error", "content": "No action specified"}

        # Check if it's an ANSWER
        if action_line.startswith("ANSWER:"):
            return {
                "type": "answer",
                "content": action_line[7:].strip(),
            }

        # Check if it's a TOOL call
        if action_line.startswith("TOOL:"):
            tool_spec = action_line[5:].strip()
            # Parse tool_name(arg1="val1", arg2="val2")
            if "(" in tool_spec:
                tool_name = tool_spec[:tool_spec.index("(")].strip()
                args_str = tool_spec[tool_spec.index("(") + 1:tool_spec.rindex(")")].strip()

                # Parse arguments (simple parser for key="value" pairs)
                args = {}
                if args_str:
                    # Split by comma but respect quotes
                    parts = self._split_args(args_str)
                    for part in parts:
                        if "=" in part:
                            key, value = part.split("=", 1)
                            key = key.strip()
                            value_str = value.strip().strip('"').strip("'")
                            # Try to convert to appropriate type
                            value_any: Any = value_str
                            if value_str.lower() == "true":
                                value_any = True
                            elif value_str.lower() == "false":
                                value_any = False
                            elif value_str.isdigit():
                                value_any = int(value_str)
                            elif value_str.startswith("[") and value_str.endswith("]"):
                                # Parse list
                                value_any = [v.strip().strip('"').strip("'") for v in value_str[1:-1].split(",")]
                            args[key] = value_any

                return {
                    "type": "tool",
                    "tool_name": tool_name,
                    "args": args,
                }

        return {"type": "error", "content": f"Could not parse action: {action_line}"}

    def _split_args(self, args_str: str) -> list[str]:
        """Split argument string by comma, respecting quotes."""
        parts = []
        current = []
        in_quotes = False
        quote_char = None

        for char in args_str:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current.append(char)
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current.append(char)
            elif char == "," and not in_quotes:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)

        if current:
            parts.append("".join(current))

        return [p.strip() for p in parts if p.strip()]

    def _execute_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a tool with given arguments.

        Args:
            tool_name: Name of the tool to execute
            args: Arguments to pass to the tool

        Returns:
            Tool execution result
        """
        try:
            if hasattr(self.tools, tool_name):
                tool_func = getattr(self.tools, tool_name)
                return tool_func(**args)  # type: ignore[no-any-return]
            else:
                return {
                    "status": "error",
                    "message": f"Unknown tool: {tool_name}",
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error executing {tool_name}: {str(e)}",
            }

