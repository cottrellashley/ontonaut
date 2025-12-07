# Codebase Indexing & Search

Ontonaut provides a powerful indexing system that allows you to register Python types with metadata for intelligent code search and navigation.

## Overview

The indexing system allows you to:
- **Register types** with custom tags and instructions
- **Extract metadata** automatically (docstrings, methods, properties)
- **Search** by name, docstring, tags, or instructions
- **Thread-safe** registry for concurrent access
- **Type serialization** for persistence

## Quick Start

### Define Custom Tags

Create your own tag taxonomy by inheriting from `IndexTag`:

```python
from ontonaut import IndexTag

class MyTags(IndexTag):
    DATABASE = "database"
    API = "api"
    UTIL = "util"
    SERVICE = "service"
    MODEL = "model"
```

### Register Types

Use the `@index_type` decorator to register types:

```python
from ontonaut import index_type

@index_type(tags=[MyTags.DATABASE, MyTags.MODEL], instructions="Main user model")
class User:
    """User model for authentication and authorization."""

    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    def authenticate(self, password: str) -> bool:
        """Authenticate user with password."""
        pass

    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return True
```

### Search the Registry

Search for registered types:

```python
from ontonaut import search_registry

# Search by query
results = search_registry("user")

# Search by tags
results = search_registry(tags=[MyTags.DATABASE])

# Combined search
results = search_registry("authentication", tags=[MyTags.MODEL])

# Require all tags
results = search_registry(tags=[MyTags.DATABASE, MyTags.MODEL], require_all_tags=True)
```

## Core Concepts

### IndexTag

Base class for creating custom tag taxonomies.

```python
class IndexTag(str, Enum):
    """Base for custom tags."""
    pass

# Usage
class ProjectTags(IndexTag):
    CORE = "core"
    PLUGIN = "plugin"
    LEGACY = "legacy"
```

**Features:**
- String-based enum
- Comparable with strings
- Serializable
- Type-safe

### RegisteredType

Container for type metadata extracted during registration.

**Attributes:**
- `cls` - The registered type
- `cls_path` - Fully qualified type path (e.g., `"myapp.models.User"`)
- `name` - Simple class name
- `module` - Module name
- `tags` - List of associated tags
- `instructions` - Custom instructions/description
- `docstring` - Class docstring
- `methods` - Public methods with metadata
- `properties` - Public properties with metadata
- `attributes` - Class-level attributes
- `bases` - Base class paths

**Methods:**
- `has_tag(tag)` - Check if type has a specific tag
- `has_any_tag(tags)` - Check if has any of the tags
- `has_all_tags(tags)` - Check if has all of the tags
- `search_methods(query)` - Search methods by name/docstring
- `search_properties(query)` - Search properties by name/docstring
- `to_dict()` - Convert to dictionary

### TypeRegistry

Thread-safe registry for storing and querying types.

**Methods:**
- `register(cls, tags, instructions)` - Register a type
- `unregister(cls)` - Remove a type
- `get(cls)` - Get registered type
- `get_all()` - Get all registered types
- `search(query, tags, require_all_tags)` - Search types
- `clear()` - Clear all registrations

## Registration Methods

### Decorator with Arguments

```python
@index_type(tags=[MyTags.API], instructions="REST API endpoint")
class UserAPI:
    """API for user management."""
    pass
```

### Decorator without Arguments

```python
@index_type
class UtilityClass:
    """Utility functions."""
    pass
```

### Function Call

```python
class LegacyClass:
    """Old legacy code."""
    pass

index_type(LegacyClass, tags=[MyTags.LEGACY], instructions="Needs refactoring")
```

## Metadata Extraction

The system automatically extracts rich metadata from registered types:

### Docstrings

```python
@index_type
class DataProcessor:
    """Process data from various sources."""

    def transform(self, data):
        """Transform input data to output format."""
        pass

# Access docstrings
registry = get_registry()
registered = registry.get(DataProcessor)
print(registered.docstring)  # "Process data from various sources."
print(registered.methods["transform"]["docstring"])  # "Transform input data..."
```

### Methods

Extracted method metadata includes:
- Docstring
- Signature
- Is classmethod
- Is staticmethod
- Is property

```python
registered = registry.get(SomeClass)
for name, info in registered.methods.items():
    print(f"{name}{info['signature']}")
    print(f"  {info['docstring']}")
    print(f"  Classmethod: {info['is_classmethod']}")
```

### Properties

```python
@index_type
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self) -> float:
        """Calculate circle area."""
        return 3.14159 * self._radius ** 2

    @area.setter
    def area(self, value: float):
        self._radius = (value / 3.14159) ** 0.5

registered = registry.get(Circle)
prop_info = registered.properties["area"]
print(prop_info["docstring"])  # "Calculate circle area."
print(prop_info["has_setter"])  # True
```

### Class Attributes

```python
@index_type
class Config:
    MAX_CONNECTIONS = 100
    TIMEOUT = 30
    DEBUG = False

registered = registry.get(Config)
for name, info in registered.attributes.items():
    print(f"{name} = {info['value']}")
```

## Searching

### Search by Query

Searches in: name, module, docstring, instructions

```python
# Case-insensitive search
results = search_registry("user")
results = search_registry("authentication")
results = search_registry("myapp.models")
```

### Search by Tags

```python
# Any tag matches
results = search_registry(tags=[MyTags.DATABASE, MyTags.API])

# All tags must match
results = search_registry(
    tags=[MyTags.DATABASE, MyTags.MODEL],
    require_all_tags=True
)
```

### Combined Search

```python
results = search_registry(
    query="user",
    tags=[MyTags.DATABASE],
    require_all_tags=False
)
```

### Search Methods/Properties

```python
registered = registry.get(MyClass)

# Find authentication-related methods
auth_methods = registered.search_methods("auth")

# Find computed properties
computed = registered.search_properties("compute")
```

## Advanced Usage

### Type Serialization

```python
# Get type path
registered = registry.get(User)
path = registered.cls_path  # "myapp.models.User"

# Recreate from path
from ontonaut.indexing import RegisteredType
restored = RegisteredType.from_path(path, tags=[MyTags.DATABASE])
```

### Registry Access

```python
from ontonaut import get_registry, clear_registry

# Get global registry
registry = get_registry()

# Check if type registered
if MyClass in registry:
    print("Registered!")

# Get count
print(f"Registered types: {len(registry)}")

# Get all types
all_types = registry.get_all()

# Clear registry (useful for testing)
clear_registry()
```

### Thread Safety

The registry is thread-safe for concurrent access:

```python
import threading

def register_types():
    for i in range(100):
        @index_type
        class DynamicClass:
            pass

threads = [threading.Thread(target=register_types) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# All types safely registered
print(len(get_registry()))
```

## Real-World Example

```python
from ontonaut import index_type, IndexTag, search_registry

# Define your taxonomy
class AppTags(IndexTag):
    DATABASE = "database"
    API = "api"
    SERVICE = "service"
    UTIL = "util"
    DEPRECATED = "deprecated"

# Register your codebase types
@index_type(tags=[AppTags.DATABASE], instructions="Primary user model")
class User:
    """User account with authentication."""

    def authenticate(self, password: str) -> bool:
        """Verify user credentials."""
        pass

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

@index_type(tags=[AppTags.API, AppTags.SERVICE], instructions="REST API for users")
class UserService:
    """Service layer for user operations."""

    def create_user(self, data: dict) -> User:
        """Create a new user."""
        pass

    def find_user(self, user_id: int) -> User:
        """Find user by ID."""
        pass

@index_type(tags=[AppTags.UTIL, AppTags.DEPRECATED], instructions="Use EmailValidator instead")
class OldEmailChecker:
    """Legacy email validation."""
    pass

# Search your codebase
# Find all database models
db_models = search_registry(tags=[AppTags.DATABASE])
for model in db_models:
    print(f"{model.name}: {model.docstring}")

# Find deprecated code
deprecated = search_registry(tags=[AppTags.DEPRECATED])
for item in deprecated:
    print(f"⚠️ {item.name}: {item.instructions}")

# Find authentication-related code
auth_types = search_registry("authentication")
for t in auth_types:
    # Get authentication methods
    auth_methods = t.search_methods("auth")
    for method_name, method_info in auth_methods.items():
        print(f"  {t.name}.{method_name}{method_info['signature']}")
```

## Integration with AI Agents

The indexing system is designed for AI agent integration:

```python
# Example: Build context for AI
def build_ai_context(query: str) -> str:
    results = search_registry(query)

    context = []
    for r in results:
        context.append(f"Class: {r.cls_path}")
        context.append(f"Description: {r.docstring}")
        context.append(f"Instructions: {r.instructions}")
        context.append("\nMethods:")
        for name, info in r.methods.items():
            context.append(f"  - {name}{info['signature']}")
            context.append(f"    {info['docstring']}")

    return "\n".join(context)

# Use in AI prompt
ai_context = build_ai_context("user authentication")
```

## Best Practices

1. **Consistent Tagging** - Define a clear tag taxonomy upfront
2. **Meaningful Instructions** - Add context that's not in the docstring
3. **Register Early** - Register types when defining them
4. **Search Smart** - Combine queries and tags for precision
5. **Document Everything** - Good docstrings = better search results
6. **Use Type Hints** - Helps with method signatures
7. **Test Coverage** - Clear registry in test fixtures

## See Also

- [Code Editor](./code-editor.md)
- [ChatBot](./chatbot.md)
- [Custom Executors](./custom-executors.md)
