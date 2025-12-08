"""
RegisteredType class that holds metadata about indexed types.
"""

from typing import Any, Optional, Union

from ontonaut.indexing.metadata import (
    extract_type_metadata,
    get_type_from_path,
)
from ontonaut.indexing.tags import IndexTag


class RegisteredType:
    """
    Represents a type that has been registered in the index.

    This class stores all metadata about a registered type including:
    - Type path (module.name)
    - Tags for categorization
    - Custom instructions
    - Docstrings
    - Public methods and properties
    - Class attributes
    """

    def __init__(
        self,
        cls: type,
        tags: Optional[list[IndexTag]] = None,
        instructions: str = "",
    ):
        """
        Initialize a registered type.

        Args:
            cls: The type to register
            tags: List of tags for categorization
            instructions: Custom instructions or description
        """
        self._cls = cls
        self._tags = tags or []
        self._instructions = instructions

        # Extract and cache all metadata
        self._metadata = extract_type_metadata(cls)

    @property
    def cls(self) -> type:
        """Get the registered type."""
        return self._cls

    @property
    def cls_path(self) -> str:
        """Get the fully qualified path of the type."""
        return self._metadata["path"]  # type: ignore[no-any-return]

    @property
    def name(self) -> str:
        """Get the simple name of the type."""
        return self._metadata["name"]  # type: ignore[no-any-return]

    @property
    def qualname(self) -> str:
        """Get the qualified name (includes parent classes)."""
        return self._metadata["qualname"]  # type: ignore[no-any-return]

    @property
    def module(self) -> str:
        """Get the module name."""
        return self._metadata["module"]  # type: ignore[no-any-return]

    @property
    def tags(self) -> list[IndexTag]:
        """Get the list of tags."""
        return self._tags

    @property
    def instructions(self) -> str:
        """Get the custom instructions."""
        return self._instructions

    @property
    def docstring(self) -> str:
        """Get the class docstring."""
        return self._metadata["docstring"]  # type: ignore[no-any-return]

    @property
    def bases(self) -> list[str]:
        """Get the base class paths."""
        return self._metadata["bases"]  # type: ignore[no-any-return]

    @property
    def methods(self) -> dict[str, dict[str, Any]]:
        """
        Get all public methods with their metadata.

        Returns:
            Dictionary mapping method names to their metadata:
            {
                "method_name": {
                    "docstring": "...",
                    "signature": "...",
                    "is_classmethod": bool,
                    "is_staticmethod": bool,
                    "is_property": bool,
                }
            }
        """
        return self._metadata["methods"]  # type: ignore[no-any-return]

    @property
    def properties(self) -> dict[str, dict[str, Any]]:
        """
        Get all public properties with their metadata.

        Returns:
            Dictionary mapping property names to their metadata:
            {
                "property_name": {
                    "docstring": "...",
                    "has_setter": bool,
                    "has_deleter": bool,
                }
            }
        """
        return self._metadata["properties"]  # type: ignore[no-any-return]

    @property
    def attributes(self) -> dict[str, Any]:
        """Get all class-level attributes."""
        return self._metadata["attributes"]  # type: ignore[no-any-return]

    @property
    def is_abstract(self) -> bool:
        """Check if the type is abstract."""
        return self._metadata["is_abstract"]  # type: ignore[no-any-return]

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the complete metadata dictionary."""
        return {
            **self._metadata,
            "tags": [str(tag) for tag in self._tags],
            "instructions": self._instructions,
        }

    def has_tag(self, tag: Union[IndexTag, str]) -> bool:
        """
        Check if this type has a specific tag.

        Args:
            tag: Tag to check for (IndexTag or string)

        Returns:
            True if the tag is present
        """
        tag_str = str(tag)
        return any(str(t) == tag_str for t in self._tags)

    def has_any_tag(self, tags: list[Union[IndexTag, str]]) -> bool:
        """
        Check if this type has any of the specified tags.

        Args:
            tags: List of tags to check for

        Returns:
            True if any tag is present
        """
        return any(self.has_tag(tag) for tag in tags)

    def has_all_tags(self, tags: list[Union[IndexTag, str]]) -> bool:
        """
        Check if this type has all of the specified tags.

        Args:
            tags: List of tags to check for

        Returns:
            True if all tags are present
        """
        return all(self.has_tag(tag) for tag in tags)

    def search_methods(self, query: str) -> dict[str, dict[str, Any]]:
        """
        Search methods by name or docstring.

        Args:
            query: Search query (case-insensitive)

        Returns:
            Dictionary of matching methods
        """
        query_lower = query.lower()
        return {
            name: info
            for name, info in self.methods.items()
            if query_lower in name.lower() or query_lower in info["docstring"].lower()
        }

    def search_properties(self, query: str) -> dict[str, dict[str, Any]]:
        """
        Search properties by name or docstring.

        Args:
            query: Search query (case-insensitive)

        Returns:
            Dictionary of matching properties
        """
        query_lower = query.lower()
        return {
            name: info
            for name, info in self.properties.items()
            if query_lower in name.lower() or query_lower in info["docstring"].lower()
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a dictionary representation.

        Returns:
            Dictionary containing all data
        """
        return {
            "cls_path": self.cls_path,
            "name": self.name,
            "module": self.module,
            "tags": [str(tag) for tag in self.tags],
            "instructions": self.instructions,
            "metadata": self.metadata,
        }

    @classmethod
    def from_path(
        cls,
        path: str,
        tags: Optional[list[IndexTag]] = None,
        instructions: str = "",
    ) -> "RegisteredType":
        """
        Create a RegisteredType from a type path.

        Args:
            path: Fully qualified type path
            tags: List of tags
            instructions: Custom instructions

        Returns:
            RegisteredType instance

        Raises:
            ImportError: If type cannot be imported
        """
        type_cls = get_type_from_path(path)
        return cls(type_cls, tags=tags, instructions=instructions)

    def __repr__(self) -> str:
        tag_str = ", ".join(str(t) for t in self._tags)
        return f"RegisteredType({self.cls_path}, tags=[{tag_str}])"

    def __str__(self) -> str:
        return f"{self.name} ({self.module})"
