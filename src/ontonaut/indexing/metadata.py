"""
Type metadata extraction utilities.
"""

import inspect
from typing import Any


def get_type_path(cls: type) -> str:
    """
    Get the fully qualified path for a type.

    Args:
        cls: The type to get the path for

    Returns:
        String in format "module.name"

    Example:
        >>> get_type_path(dict)
        'builtins.dict'
    """
    module = cls.__module__
    name = cls.__qualname__
    return f"{module}.{name}"


def get_type_from_path(path: str) -> type:
    """
    Reconstruct a type from its fully qualified path.

    Args:
        path: String in format "module.name"

    Returns:
        The type object

    Raises:
        ImportError: If module cannot be imported
        AttributeError: If type not found in module
    """
    parts = path.rsplit(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid type path: {path}")

    module_name, type_name = parts

    # Import the module
    import importlib

    module = importlib.import_module(module_name)

    # Get the type from the module
    # Handle nested classes
    type_parts = type_name.split(".")
    obj: Any = module
    for part in type_parts:
        obj = getattr(obj, part)

    return obj  # type: ignore[no-any-return]


def extract_docstring(obj: Any) -> str:
    """
    Extract docstring from an object, handling None cases.

    Args:
        obj: Object to extract docstring from

    Returns:
        Docstring or empty string if none exists
    """
    doc = inspect.getdoc(obj)
    return doc if doc else ""


def extract_public_methods(cls: type) -> dict[str, dict[str, Any]]:
    """
    Extract all public methods from a class with their metadata.

    Args:
        cls: The class to extract methods from

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
    methods = {}

    for name, value in inspect.getmembers(cls):
        # Skip private methods
        if name.startswith("_"):
            continue

        # Check if it's a method, classmethod, staticmethod, or property
        is_method = inspect.ismethod(value) or inspect.isfunction(value)
        is_property = isinstance(inspect.getattr_static(cls, name), property)
        is_classmethod = isinstance(inspect.getattr_static(cls, name), classmethod)
        is_staticmethod = isinstance(inspect.getattr_static(cls, name), staticmethod)

        if is_method or is_property or is_classmethod or is_staticmethod:
            method_info = {
                "docstring": extract_docstring(value),
                "is_classmethod": is_classmethod,
                "is_staticmethod": is_staticmethod,
                "is_property": is_property,
            }

            # Get signature for methods (not properties)
            if not is_property:
                try:
                    sig = inspect.signature(value)
                    method_info["signature"] = str(sig)
                except (ValueError, TypeError):
                    method_info["signature"] = "()"
            else:
                method_info["signature"] = None

            methods[name] = method_info

    return methods


def extract_public_properties(cls: type) -> dict[str, dict[str, Any]]:
    """
    Extract all public properties from a class with their metadata.

    Args:
        cls: The class to extract properties from

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
    properties = {}

    for name in dir(cls):
        # Skip private attributes
        if name.startswith("_"):
            continue

        try:
            attr = inspect.getattr_static(cls, name)
            if isinstance(attr, property):
                properties[name] = {
                    "docstring": extract_docstring(attr.fget) if attr.fget else "",
                    "has_setter": attr.fset is not None,
                    "has_deleter": attr.fdel is not None,
                }
        except AttributeError:
            continue

    return properties


def extract_class_attributes(cls: type) -> dict[str, Any]:
    """
    Extract class-level attributes (non-methods, non-properties).

    Args:
        cls: The class to extract attributes from

    Returns:
        Dictionary mapping attribute names to their types
    """
    attributes = {}

    for name, value in inspect.getmembers(cls):
        # Skip private attributes
        if name.startswith("_"):
            continue

        # Skip methods and properties
        if (
            inspect.ismethod(value)
            or inspect.isfunction(value)
            or isinstance(inspect.getattr_static(cls, name), property)
        ):
            continue

        # Get type hint if available
        type_hint = None
        if hasattr(cls, "__annotations__") and name in cls.__annotations__:
            type_hint = cls.__annotations__[name]

        attributes[name] = {
            "value": repr(value) if not callable(value) else "<callable>",
            "type": type_hint,
        }

    return attributes


def extract_type_metadata(cls: type) -> dict[str, Any]:
    """
    Extract comprehensive metadata from a type.

    Args:
        cls: The type to extract metadata from

    Returns:
        Dictionary containing all extracted metadata
    """
    return {
        "path": get_type_path(cls),
        "name": cls.__name__,
        "qualname": cls.__qualname__,
        "module": cls.__module__,
        "docstring": extract_docstring(cls),
        "bases": [get_type_path(base) for base in cls.__bases__ if base is not object],
        "methods": extract_public_methods(cls),
        "properties": extract_public_properties(cls),
        "attributes": extract_class_attributes(cls),
        "is_abstract": inspect.isabstract(cls),
    }
