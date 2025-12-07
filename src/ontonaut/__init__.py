"""Ontonaut - Customizable widgets for marimo with pluggable execution backends."""

__version__ = "0.2.0"
__author__ = "Ashley Cottrell"
__email__ = "your.email@example.com"

# Code Editor
# Chat Bot
from ontonaut.chatbot import ChatBot
from ontonaut.codebase_agent import CodebaseAgent
from ontonaut.editor import CodeEditor
from ontonaut.executors import PythonExecutor, create_executor
from ontonaut.handlers import (
    AnthropicHandler,
    BaseHandler,
    CustomHandler,
    EchoHandler,
    MCPHandler,
    OpenAIHandler,
    create_handler,
)

# Indexing / Search
from ontonaut.indexing import (
    IndexTag,
    RegisteredType,
    clear_registry,
    get_registry,
    index_type,
    register_type,
    search_registry,
)

__all__ = [
    # Editor
    "CodeEditor",
    "PythonExecutor",
    "create_executor",
    # ChatBot
    "ChatBot",
    "BaseHandler",
    "EchoHandler",
    "OpenAIHandler",
    "AnthropicHandler",
    "MCPHandler",
    "CustomHandler",
    "create_handler",
    # Codebase Agent
    "CodebaseAgent",
    # Indexing
    "register_type",
    "index_type",
    "IndexTag",
    "RegisteredType",
    "get_registry",
    "clear_registry",
    "search_registry",
    # Meta
    "__version__",
]
