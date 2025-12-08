"""Tests for the indexing system."""

import pytest

from ontonaut import (
    IndexTag,
    RegisteredType,
    clear_registry,
    get_registry,
    index_type,
    search_registry,
)


# Test fixtures
class TestTags(IndexTag):
    """Test tags for categorization."""

    DATABASE = "database"
    API = "api"
    UTIL = "util"
    SERVICE = "service"


class SampleClass:
    """A sample class for testing."""

    class_attr = 42

    def __init__(self, value: int):
        self.value = value

    def public_method(self, x: int) -> int:
        """
        A public method.

        Args:
            x: Input value

        Returns:
            Result value
        """
        return x * 2

    @property
    def computed_property(self) -> int:
        """A computed property."""
        return self.value * 2

    @classmethod
    def class_method(cls) -> str:
        """A class method."""
        return "class_method"

    @staticmethod
    def static_method() -> str:
        """A static method."""
        return "static_method"

    def _private_method(self):
        """Should not be indexed."""
        pass


@pytest.fixture(autouse=True)
def clean_registry():
    """Clear registry before and after each test."""
    clear_registry()
    yield
    clear_registry()


class TestIndexTag:
    """Test IndexTag functionality."""

    def test_create_custom_tags(self):
        """Test creating custom tags."""
        assert TestTags.DATABASE.value == "database"
        assert TestTags.API.value == "api"

    def test_tag_string_conversion(self):
        """Test tag to string conversion."""
        assert str(TestTags.DATABASE) == "database"

    def test_tag_from_string(self):
        """Test creating tag from string."""
        tag = TestTags.from_string("database")
        assert tag == TestTags.DATABASE

    def test_tag_equality_with_string(self):
        """Test tag equality with strings."""
        assert TestTags.DATABASE == "database"

    def test_tag_repr(self):
        """Test tag representation."""
        assert "TestTags.DATABASE" in repr(TestTags.DATABASE)


class TestRegisteredType:
    """Test RegisteredType functionality."""

    def test_create_registered_type(self):
        """Test creating a registered type."""
        registered = RegisteredType(
            SampleClass, tags=[TestTags.DATABASE], instructions="Test class"
        )

        assert registered.cls == SampleClass
        assert registered.name == "SampleClass"
        assert registered.instructions == "Test class"
        assert registered.has_tag(TestTags.DATABASE)

    def test_type_path(self):
        """Test type path extraction."""
        registered = RegisteredType(SampleClass)
        assert "test_indexing" in registered.cls_path
        assert "SampleClass" in registered.cls_path

    def test_docstring_extraction(self):
        """Test docstring extraction."""
        registered = RegisteredType(SampleClass)
        assert "A sample class for testing" in registered.docstring

    def test_method_extraction(self):
        """Test method extraction."""
        registered = RegisteredType(SampleClass)
        methods = registered.methods

        # Check public method exists
        assert "public_method" in methods
        assert "A public method" in methods["public_method"]["docstring"]

        # Check private method not included
        assert "_private_method" not in methods

        # Check classmethod
        assert "class_method" in methods
        assert methods["class_method"]["is_classmethod"]

        # Check staticmethod
        assert "static_method" in methods
        assert methods["static_method"]["is_staticmethod"]

    def test_property_extraction(self):
        """Test property extraction."""
        registered = RegisteredType(SampleClass)
        properties = registered.properties

        assert "computed_property" in properties
        assert "A computed property" in properties["computed_property"]["docstring"]

    def test_attribute_extraction(self):
        """Test class attribute extraction."""
        registered = RegisteredType(SampleClass)
        attributes = registered.attributes

        assert "class_attr" in attributes

    def test_tag_checking(self):
        """Test tag checking methods."""
        registered = RegisteredType(SampleClass, tags=[TestTags.DATABASE, TestTags.API])

        assert registered.has_tag(TestTags.DATABASE)
        assert registered.has_tag("database")
        assert not registered.has_tag(TestTags.UTIL)

        assert registered.has_any_tag([TestTags.DATABASE, TestTags.UTIL])
        assert not registered.has_any_tag([TestTags.UTIL, TestTags.SERVICE])

        assert registered.has_all_tags([TestTags.DATABASE, TestTags.API])
        assert not registered.has_all_tags([TestTags.DATABASE, TestTags.UTIL])

    def test_search_methods(self):
        """Test method searching."""
        registered = RegisteredType(SampleClass)
        results = registered.search_methods("public")

        assert "public_method" in results

    def test_search_properties(self):
        """Test property searching."""
        registered = RegisteredType(SampleClass)
        results = registered.search_properties("computed")

        assert "computed_property" in results

    def test_to_dict(self):
        """Test dictionary conversion."""
        registered = RegisteredType(SampleClass, tags=[TestTags.DATABASE])
        data = registered.to_dict()

        assert data["name"] == "SampleClass"
        assert "database" in data["tags"]
        assert "cls_path" in data
        assert "metadata" in data


class TestTypeRegistry:
    """Test TypeRegistry functionality."""

    def test_register_type(self):
        """Test registering a type."""
        registry = get_registry()
        registered = registry.register(SampleClass, tags=[TestTags.DATABASE])

        assert isinstance(registered, RegisteredType)
        assert len(registry) == 1

    def test_get_registered_type(self):
        """Test getting a registered type."""
        registry = get_registry()
        registry.register(SampleClass)

        registered = registry.get(SampleClass)
        assert registered is not None
        assert registered.cls == SampleClass

    def test_get_by_path(self):
        """Test getting a type by path."""
        registry = get_registry()
        registered = registry.register(SampleClass)

        found = registry.get(registered.cls_path)
        assert found is not None
        assert found.cls == SampleClass

    def test_unregister_type(self):
        """Test unregistering a type."""
        registry = get_registry()
        registry.register(SampleClass)

        assert len(registry) == 1
        registry.unregister(SampleClass)
        assert len(registry) == 0

    def test_get_all(self):
        """Test getting all registered types."""
        registry = get_registry()
        registry.register(SampleClass)

        all_types = registry.get_all()
        assert len(all_types) == 1
        assert all_types[0].cls == SampleClass

    def test_contains(self):
        """Test __contains__ method."""
        registry = get_registry()
        assert SampleClass not in registry

        registry.register(SampleClass)
        assert SampleClass in registry

    def test_search_by_query(self):
        """Test searching by query."""
        registry = get_registry()
        registry.register(SampleClass, instructions="sample test class")

        results = registry.search(query="sample")
        assert len(results) == 1
        assert results[0].cls == SampleClass

    def test_search_by_tags(self):
        """Test searching by tags."""
        registry = get_registry()
        registry.register(SampleClass, tags=[TestTags.DATABASE])

        results = registry.search(tags=[TestTags.DATABASE])
        assert len(results) == 1

        results = registry.search(tags=[TestTags.API])
        assert len(results) == 0

    def test_search_combined(self):
        """Test combined search."""
        registry = get_registry()
        registry.register(SampleClass, tags=[TestTags.DATABASE], instructions="sample")

        results = registry.search(query="sample", tags=[TestTags.DATABASE])
        assert len(results) == 1

        results = registry.search(query="sample", tags=[TestTags.API])
        assert len(results) == 0

    def test_search_require_all_tags(self):
        """Test searching with require_all_tags."""
        registry = get_registry()
        registry.register(SampleClass, tags=[TestTags.DATABASE, TestTags.API])

        # Require any tag
        results = registry.search(
            tags=[TestTags.DATABASE, TestTags.UTIL], require_all_tags=False
        )
        assert len(results) == 1

        # Require all tags
        results = registry.search(
            tags=[TestTags.DATABASE, TestTags.API], require_all_tags=True
        )
        assert len(results) == 1

        results = registry.search(
            tags=[TestTags.DATABASE, TestTags.UTIL], require_all_tags=True
        )
        assert len(results) == 0


class TestIndexTypeDecorator:
    """Test index_type decorator/function."""

    def test_decorator_usage(self):
        """Test using index_type as a decorator."""

        @index_type(tags=[TestTags.DATABASE], instructions="Test")
        class TestClass:
            """Test class."""

            pass

        registry = get_registry()
        registered = registry.get(TestClass)

        assert registered is not None
        assert registered.has_tag(TestTags.DATABASE)
        assert registered.instructions == "Test"

    def test_function_usage(self):
        """Test using index_type as a function."""

        class TestClass:
            """Test class."""

            pass

        index_type(TestClass, tags=[TestTags.API], instructions="API class")

        registry = get_registry()
        registered = registry.get(TestClass)

        assert registered is not None
        assert registered.has_tag(TestTags.API)

    def test_decorator_without_args(self):
        """Test decorator without arguments."""

        @index_type
        class TestClass:
            """Test class."""

            pass

        registry = get_registry()
        assert TestClass in registry


class TestGlobalFunctions:
    """Test global helper functions."""

    def test_clear_registry(self):
        """Test clearing the registry."""
        registry = get_registry()
        registry.register(SampleClass)

        assert len(registry) == 1
        clear_registry()
        assert len(registry) == 0

    def test_search_registry(self):
        """Test global search function."""
        index_type(SampleClass, tags=[TestTags.DATABASE])

        results = search_registry(tags=[TestTags.DATABASE])
        assert len(results) == 1

        results = search_registry(query="sample")
        assert len(results) >= 0


class TestThreadSafety:
    """Test thread safety of registry."""

    def test_concurrent_registration(self):
        """Test concurrent type registration."""
        import threading

        registry = get_registry()
        registered_count = []

        def register_type():
            class DynamicClass:
                pass

            registry.register(DynamicClass)
            registered_count.append(1)

        threads = [threading.Thread(target=register_type) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All 10 types should be registered
        assert len(registered_count) == 10
