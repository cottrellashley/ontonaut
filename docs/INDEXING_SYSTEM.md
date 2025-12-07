# Ontonaut Indexing System

## Overview

The Ontonaut Indexing System is a powerful codebase search and metadata extraction feature that allows developers to register Python types with custom tags and instructions, enabling intelligent code navigation and AI agent integration.

## Architecture

### Module Structure

```
src/ontonaut/indexing/
├── __init__.py              # Public API exports
├── tags.py                  # IndexTag base class
├── metadata.py              # Type metadata extraction utilities
├── registered_type.py       # RegisteredType container class
└── registry.py              # Thread-safe global registry
```

### Core Components

#### 1. IndexTag (`tags.py`)
- Base class for creating custom tag taxonomies
- Inherits from `str` and `Enum`
- Provides string equality and serialization
- Users extend this to define their own tags

#### 2. RegisteredType (`registered_type.py`)
- Container for registered type metadata
- Stores: type path, tags, instructions, docstrings, methods, properties
- Provides search and query methods
- Automatically extracts metadata on initialization

#### 3. TypeRegistry (`registry.py`)
- Thread-safe registry using `threading.RLock()`
- Global singleton instance `_index_register`
- Supports registration, search, and retrieval
- Concurrent access safe

#### 4. Metadata Extraction (`metadata.py`)
- **Type Serialization**: `get_type_path()`, `get_type_from_path()`
- **Docstring Extraction**: `extract_docstring()`
- **Method Extraction**: `extract_public_methods()`
- **Property Extraction**: `extract_public_properties()`
- **Attribute Extraction**: `extract_class_attributes()`
- **Full Metadata**: `extract_type_metadata()`

## User-Facing API

### Registration

```python
from ontonaut import index_type, IndexTag

# Define tags
class MyTags(IndexTag):
    DATABASE = "database"
    API = "api"

# Register as decorator
@index_type(tags=[MyTags.DATABASE], instructions="Main user model")
class User:
    """User authentication model."""
    pass

# Register as function
index_type(User, tags=[MyTags.DATABASE], instructions="...")
```

### Search

```python
from ontonaut import search_registry

# Search by query
results = search_registry("user")

# Search by tags
results = search_registry(tags=[MyTags.DATABASE])

# Combined
results = search_registry("auth", tags=[MyTags.API])

# Require all tags
results = search_registry(tags=[MyTags.DB, MyTags.API], require_all_tags=True)
```

### Registry Access

```python
from ontonaut import get_registry, clear_registry

registry = get_registry()
registered = registry.get(User)

# Access metadata
print(registered.cls_path)
print(registered.docstring)
print(registered.methods)
print(registered.properties)
```

## Implementation Details

### Thread Safety

- Uses `threading.RLock()` for reentrant locking
- All registry operations are atomic
- Safe for concurrent registration and search

### Metadata Extraction Process

1. **Type Path**: Extract `__module__` and `__qualname__`
2. **Docstring**: Use `inspect.getdoc()` for cleaned docstrings
3. **Methods**: Use `inspect.getmembers()` with type checking
4. **Signatures**: Extract via `inspect.signature()`
5. **Properties**: Detect using `inspect.getattr_static()`
6. **Bases**: Extract base class paths recursively

### Search Algorithm

```python
def search(query, tags, require_all_tags):
    results = all_registered_types

    # Filter by tags
    if tags:
        if require_all_tags:
            results = filter(has_all_tags, results)
        else:
            results = filter(has_any_tag, results)

    # Filter by query (case-insensitive)
    if query:
        results = filter(matches_query, results)

    return results
```

## Testing

### Test Coverage

- **31 tests** covering all functionality
- **96%+ coverage** for core modules
- Tests for thread safety, serialization, search

### Test Structure

```
tests/test_indexing.py
├── TestIndexTag              # Tag creation and comparison
├── TestRegisteredType        # Metadata extraction
├── TestTypeRegistry          # Registry operations
├── TestIndexTypeDecorator    # Decorator usage
├── TestGlobalFunctions       # Helper functions
└── TestThreadSafety          # Concurrent access
```

## Performance Considerations

### Metadata Extraction
- Performed once at registration time
- Cached in `RegisteredType` instance
- No runtime overhead for searches

### Search Performance
- O(n) linear scan of registered types
- Filter by tags first (smaller set)
- Case-insensitive string matching

### Memory Usage
- One `RegisteredType` instance per registered type
- Metadata stored as dictionaries
- Minimal overhead (~1-2KB per type)

## Use Cases

### 1. AI Agent Integration
```python
# Build context for AI
results = search_registry("authentication")
context = "\n".join(r.docstring for r in results)
```

### 2. Code Navigation
```python
# Find all database models
models = search_registry(tags=[MyTags.DATABASE])

# Find deprecated code
deprecated = search_registry(tags=[MyTags.DEPRECATED])
```

### 3. Documentation Generation
```python
# Generate API docs
for r in search_registry(tags=[MyTags.API]):
    print(f"# {r.name}")
    print(r.docstring)
    for method, info in r.methods.items():
        print(f"## {method}{info['signature']}")
```

### 4. Architecture Analysis
```python
# Find all services
services = search_registry(tags=[MyTags.SERVICE])

# Analyze dependencies
for s in services:
    print(f"{s.name} extends: {', '.join(s.bases)}")
```

## Future Enhancements

### Potential Features
- **Persistence**: Save registry to disk
- **Incremental Updates**: Watch for file changes
- **Cross-References**: Link related types
- **Call Graph**: Track method calls
- **Type Hints**: Extract and index type annotations
- **Decorators**: Index decorators and their targets
- **Fuzzy Search**: Approximate string matching
- **Search Ranking**: Score results by relevance

### Integration Opportunities
- **Language Server Protocol (LSP)**: Code completion
- **Static Analysis**: Combine with AST parsing
- **Documentation Tools**: Generate from index
- **CI/CD**: Enforce tagging policies

## Best Practices

### For Library Users

1. **Define Clear Tags**: Create a consistent taxonomy
2. **Add Instructions**: Provide context beyond docstrings
3. **Document Everything**: Good docs = better search
4. **Register Early**: Use decorators at definition time
5. **Test Registry**: Clear in test fixtures

### For Library Developers

1. **Thread Safety**: Always use locks
2. **Error Handling**: Graceful failures for missing types
3. **Performance**: Cache expensive operations
4. **Testing**: Comprehensive coverage
5. **Documentation**: Clear examples

## API Reference

### Main Functions

- `index_type(cls, tags, instructions)` - Register a type
- `search_registry(query, tags, require_all_tags)` - Search types
- `get_registry()` - Get global registry
- `clear_registry()` - Clear all registrations

### Classes

- `IndexTag` - Base for custom tags
- `RegisteredType` - Metadata container
- `TypeRegistry` - Thread-safe registry

## Examples

See:
- `/book/markdown/indexing.md` - Full user guide
- `/book/marimo/04-indexing-search.py` - Interactive examples
- `/tests/test_indexing.py` - Comprehensive tests

## Technical Specifications

- **Python Version**: 3.9+
- **Dependencies**: Standard library only
- **Thread Safety**: Yes (RLock-based)
- **Type Safety**: Yes (full type hints)
- **Testing**: 31 tests, 96%+ coverage
- **Documentation**: Complete with examples
