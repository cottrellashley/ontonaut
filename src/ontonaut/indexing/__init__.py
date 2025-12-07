"""
Ontonaut Indexing System

A codebase search and indexing system that allows developers to register types
with metadata for intelligent code navigation and search.
"""

from ontonaut.indexing.registered_type import RegisteredType
from ontonaut.indexing.registry import (
    clear_registry,
    get_registry,
    index_type,
    register_type,
    search_registry,
)
from ontonaut.indexing.tags import IndexTag

__all__ = [
    "register_type",
    "index_type",
    "get_registry",
    "clear_registry",
    "search_registry",
    "RegisteredType",
    "IndexTag",
]
