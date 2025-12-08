"""
Agent tools for iterative codebase exploration.

Provides structured tools that an AI agent can use to explore
and understand a codebase through the indexing system.
"""

from typing import Any, Optional

from ontonaut.indexing import get_registry, search_registry


class AgentTools:
    """
    Collection of tools an AI agent can use to explore the codebase.

    Each tool returns structured data that the agent can reason about.
    """

    @staticmethod
    def search_types(
        query: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: int = 5
    ) -> dict[str, Any]:
        """
        Search for types in the codebase.

        Args:
            query: Text query to search in names/docstrings
            tags: List of tag strings to filter by
            limit: Maximum number of results

        Returns:
            Dictionary with search results and metadata
        """
        # Convert tag strings to IndexTag objects if possible
        tag_objects: Optional[list[Any]] = None
        if tags:
            tag_objects = []
            for tag_str in tags:
                # Try to find matching tags in registry
                all_types = get_registry().get_all()
                for t in all_types:
                    for t_tag in t.tags:
                        if str(t_tag).lower() == tag_str.lower():
                            tag_objects.append(t_tag)
                            break

        # Search registry
        results = search_registry(query=query, tags=tag_objects)[:limit]

        # Format results
        formatted_results = []
        for r in results:
            formatted_results.append({
                "name": r.name,
                "path": r.cls_path,
                "module": r.module,
                "docstring": r.docstring[:200] + "..." if len(r.docstring) > 200 else r.docstring,
                "tags": [str(t) for t in r.tags],
                "method_count": len(r.methods),
                "property_count": len(r.properties),
            })

        return {
            "status": "success",
            "count": len(formatted_results),
            "results": formatted_results,
            "query": query,
            "tags": tags,
        }

    @staticmethod
    def get_type_details(type_path: str) -> dict[str, Any]:
        """
        Get full details about a specific type.

        Args:
            type_path: Full path to the type (e.g., "mymodule.MyClass")

        Returns:
            Dictionary with complete type information
        """
        registry = get_registry()
        registered_type = registry.get(type_path)

        if not registered_type:
            return {
                "status": "error",
                "message": f"Type '{type_path}' not found in registry",
            }

        # Get method details
        methods = []
        for method_name, method_info in registered_type.methods.items():
            methods.append({
                "name": method_name,
                "signature": method_info.get("signature", "()"),
                "docstring": method_info.get("docstring", ""),
            })

        # Get property details
        properties = []
        for prop_name, prop_info in registered_type.properties.items():
            properties.append({
                "name": prop_name,
                "docstring": prop_info.get("docstring", ""),
            })

        return {
            "status": "success",
            "name": registered_type.name,
            "path": registered_type.cls_path,
            "module": registered_type.module,
            "docstring": registered_type.docstring,
            "instructions": registered_type.instructions,
            "tags": [str(t) for t in registered_type.tags],
            "methods": methods,
            "properties": properties,
            "attributes": registered_type.attributes,
        }

    @staticmethod
    def search_methods_in_type(type_path: str, query: str) -> dict[str, Any]:
        """
        Search for methods within a specific type.

        Args:
            type_path: Full path to the type
            query: Search query for method names

        Returns:
            Dictionary with matching methods
        """
        registry = get_registry()
        registered_type = registry.get(type_path)

        if not registered_type:
            return {
                "status": "error",
                "message": f"Type '{type_path}' not found",
            }

        # Search for methods
        matching_methods = registered_type.search_methods(query)

        # Format results
        methods = []
        for method_name in matching_methods:
            method_info = registered_type.methods[method_name]
            methods.append({
                "name": method_name,
                "signature": method_info.get("signature", "()"),
                "docstring": method_info.get("docstring", ""),
            })

        return {
            "status": "success",
            "type_path": type_path,
            "query": query,
            "count": len(methods),
            "methods": methods,
        }

    @staticmethod
    def list_all_tags() -> dict[str, Any]:
        """
        List all unique tags in the registry.

        Returns:
            Dictionary with all tags and their usage count
        """
        all_types = get_registry().get_all()
        tag_counts: dict[str, int] = {}

        for t in all_types:
            for tag in t.tags:
                tag_str = str(tag)
                tag_counts[tag_str] = tag_counts.get(tag_str, 0) + 1

        return {
            "status": "success",
            "total_unique_tags": len(tag_counts),
            "tags": [
                {"tag": tag, "count": count}
                for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            ],
        }

    @staticmethod
    def get_type_count() -> dict[str, Any]:
        """
        Get total count of indexed types.

        Returns:
            Dictionary with count information
        """
        all_types = get_registry().get_all()

        return {
            "status": "success",
            "total_types": len(all_types),
            "types_by_module": {},
        }

    @classmethod
    def get_available_tools(cls) -> list[dict[str, str]]:
        """Get list of available tools with descriptions."""
        return [
            {
                "name": "search_types",
                "description": "Search for types by query text or tags. Use this to find relevant classes.",
                "args": "query (str, optional), tags (list[str], optional), limit (int, default=5)",
            },
            {
                "name": "get_type_details",
                "description": "Get complete details about a specific type including all methods and properties.",
                "args": "type_path (str, required)",
            },
            {
                "name": "search_methods_in_type",
                "description": "Search for specific methods within a type.",
                "args": "type_path (str, required), query (str, required)",
            },
            {
                "name": "list_all_tags",
                "description": "List all available tags in the codebase with usage counts.",
                "args": "None",
            },
            {
                "name": "get_type_count",
                "description": "Get total count of indexed types in the registry.",
                "args": "None",
            },
        ]

