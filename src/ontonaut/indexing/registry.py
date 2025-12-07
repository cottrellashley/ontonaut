"""
Thread-safe registry for indexed types.
"""

import threading
from typing import Callable

from ontonaut.indexing.registered_type import RegisteredType
from ontonaut.indexing.tags import IndexTag


class TypeRegistry:
    """
    Thread-safe registry for storing and querying registered types.
    """

    def __init__(self) -> None:
        self._registry: dict[str, RegisteredType] = {}
        self._lock = threading.RLock()

    def register(
        self,
        cls: type,
        tags: list[IndexTag] | None = None,
        instructions: str = "",
    ) -> RegisteredType:
        """
        Register a type in the registry.

        Args:
            cls: The type to register
            tags: List of tags for categorization
            instructions: Custom instructions or description

        Returns:
            The RegisteredType instance
        """
        with self._lock:
            registered = RegisteredType(cls, tags=tags, instructions=instructions)
            self._registry[registered.cls_path] = registered
            return registered

    def unregister(self, cls: type | str) -> None:
        """
        Unregister a type from the registry.

        Args:
            cls: The type or type path to unregister
        """
        with self._lock:
            if isinstance(cls, str):
                path = cls
            else:
                from ontonaut.indexing.metadata import get_type_path

                path = get_type_path(cls)

            if path in self._registry:
                del self._registry[path]

    def get(self, cls: type | str) -> RegisteredType | None:
        """
        Get a registered type.

        Args:
            cls: The type or type path to get

        Returns:
            RegisteredType if found, None otherwise
        """
        with self._lock:
            if isinstance(cls, str):
                path = cls
            else:
                from ontonaut.indexing.metadata import get_type_path

                path = get_type_path(cls)

            return self._registry.get(path)

    def get_all(self) -> list[RegisteredType]:
        """Get all registered types."""
        with self._lock:
            return list(self._registry.values())

    def search(
        self,
        query: str | None = None,
        tags: list[IndexTag | str] | None = None,
        require_all_tags: bool = False,
    ) -> list[RegisteredType]:
        """
        Search registered types.

        Args:
            query: Search query (searches name, docstring, instructions)
            tags: Filter by tags
            require_all_tags: If True, require all tags; if False, require any tag

        Returns:
            List of matching RegisteredType instances
        """
        with self._lock:
            results = list(self._registry.values())

            # Filter by tags
            if tags:
                if require_all_tags:
                    results = [r for r in results if r.has_all_tags(tags)]
                else:
                    results = [r for r in results if r.has_any_tag(tags)]

            # Filter by query
            if query:
                query_lower = query.lower()
                results = [
                    r
                    for r in results
                    if (
                        query_lower in r.name.lower()
                        or query_lower in r.docstring.lower()
                        or query_lower in r.instructions.lower()
                        or query_lower in r.module.lower()
                    )
                ]

            return results

    def clear(self) -> None:
        """Clear all registered types."""
        with self._lock:
            self._registry.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._registry)

    def __contains__(self, cls: type | str) -> bool:
        return self.get(cls) is not None

    def __repr__(self) -> str:
        with self._lock:
            return f"TypeRegistry(registered={len(self._registry)})"


# Global registry instance
_index_register = TypeRegistry()


def register_type(
    typ: type,
    tags: list[IndexTag] | None = None,
    instructions: str = "",
) -> RegisteredType:
    """
    Register a type in the global index.

    This is the primary user-facing API for registering types.

    Usage:
        ```python
        from ontonaut import register_type, IndexTag

        class MyTags(IndexTag):
            DATABASE = "database"

        class User:
            '''User model for authentication.'''
            pass

        register_type(
            typ=User,
            tags=[MyTags.DATABASE],
            instructions="Main user model"
        )
        ```

    Args:
        typ: The type to register
        tags: List of tags for categorization
        instructions: Custom instructions or description

    Returns:
        The RegisteredType instance
    """
    return _index_register.register(typ, tags=tags, instructions=instructions)


def index_type(
    cls: type | None = None,
    *,
    tags: list[IndexTag] | None = None,
    instructions: str = "",
) -> Callable[[type], type] | type:
    """
    Register a type in the index (decorator style).

    Note: register_type() is the recommended explicit API.
    This decorator is provided for convenience.

    Usage as decorator:
        ```python
        @index_type(tags=[MyTags.DATABASE], instructions="Main user model")
        class User:
            '''User model for authentication.'''
            pass
        ```

    Usage as function:
        ```python
        index_type(User, tags=[MyTags.DATABASE], instructions="...")
        ```

    Args:
        cls: The type to register (when used as function)
        tags: List of tags for categorization
        instructions: Custom instructions or description

    Returns:
        Decorator function if used as decorator, type if used as function
    """

    def decorator(type_cls: type) -> type:
        _index_register.register(type_cls, tags=tags, instructions=instructions)
        return type_cls

    if cls is None:
        # Used as @index_type(tags=..., instructions=...)
        return decorator
    else:
        # Used as index_type(MyClass, tags=..., instructions=...)
        return decorator(cls)


def get_registry() -> TypeRegistry:
    """
    Get the global type registry.

    Returns:
        The global TypeRegistry instance
    """
    return _index_register


def clear_registry() -> None:
    """
    Clear all registered types from the global registry.

    Useful for testing or resetting state.
    """
    _index_register.clear()


def search_registry(
    query: str | None = None,
    tags: list[IndexTag | str] | None = None,
    require_all_tags: bool = False,
) -> list[RegisteredType]:
    """
    Search the global registry for types.

    Args:
        query: Search query (searches name, docstring, instructions)
        tags: Filter by tags
        require_all_tags: If True, require all tags; if False, require any tag

    Returns:
        List of matching RegisteredType instances

    Example:
        ```python
        # Search by query
        results = search_registry("user")

        # Search by tags
        results = search_registry(tags=[MyTags.DATABASE])

        # Combined search
        results = search_registry("model", tags=[MyTags.DATABASE])
        ```
    """
    return _index_register.search(
        query=query, tags=tags, require_all_tags=require_all_tags
    )
