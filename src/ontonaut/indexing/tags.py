"""
Index tags for categorizing registered types.
"""

from enum import Enum
from typing import Any


class IndexTag(str, Enum):
    """
    Base class for creating custom index tags.

    Users should inherit from this class to define their own tag taxonomy.

    Example:
        ```python
        class MyTags(IndexTag):
            DATABASE = "database"
            API = "api"
            UTIL = "util"
            SERVICE = "service"
        ```
    """

    def __str__(self) -> str:
        return self.value  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    @classmethod
    def from_string(cls, value: str) -> "IndexTag":
        """Create tag from string value."""
        for tag in cls:
            if tag.value == value:
                return tag
        raise ValueError(f"No {cls.__name__} with value '{value}'")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.value == other  # type: ignore[no-any-return]
        return super().__eq__(other)

    def __hash__(self) -> int:
        return hash(self.value)
