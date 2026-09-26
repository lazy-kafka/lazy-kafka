# Testing Guide for Lazy-Kafka

This document provides guidelines for testing lazy-kafka, including test structure, testing strategies, and best practices.

---

## 📋 Table of Contents

- [Test Philosophy](#-test-philosophy)
- [Test Structure](#-test-structure)
- [Running Tests](#-running-tests)
- [Writing Tests](#-writing-tests)
- [Test Types](#-test-types)
- [Mocking Strategies](#-mocking-strategies)
- [Fixtures](#-fixtures)
- [Coverage](#-coverage)
- [Best Practices](#-best-practices)

---

## 🎯 Test Philosophy

Lazy-Kafka aims for **80-90% test coverage** with a focus on:

1. **Reliability**: Tests should catch regressions and ensure core functionality works
2. **Maintainability**: Tests should be easy to understand and update
3. **Performance**: Tests should run quickly in CI/CD
4. **Completeness**: All critical paths should be tested

---

## 📁 Test Structure

```
tests/
├── __init__.py              # Test utilities and constants
├── conftest.py             # Pytest fixtures (shared across tests)
├── unit/                   # Unit tests (isolated components)
│   ├── __init__.py
│   ├── test_config.py      # Configuration tests
│   ├── test_topic.py       # Kafka client tests
│   ├── test_registry.py    # Schema Registry tests
│   ├── test_connect.py     # Kafka Connect tests
│   └── test_plugin.py      # Plugin system tests
├── integration/            # Integration tests (component interactions)
│   ├── __init__.py
│   ├── test_cli.py         # CLI command tests
│   └── test_tui.py         # TUI integration tests
├── e2e/                    # End-to-end tests (full system)
│   ├── __init__.py
│   └── test_workflows.py   # Complete workflow tests
└── fixtures/                # Test fixtures (if complex)
    └── __init__.py
```

---

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests
uv run --with pytest pytest

# Run tests with verbose output
uv run --with pytest pytest -v

# Run tests with coverage
uv run --with pytest pytest --cov=src/lazy_kafka --cov-report=term-missing

# Run a specific test file
uv run --with pytest pytest tests/unit/test_config.py

# Run a specific test function
uv run --with pytest pytest tests/unit/test_config.py::test_configuration_from_toml

# Run tests matching a pattern
uv run --with pytest pytest -k "test_config"
```

### With Coverage

```bash
# Generate coverage report (terminal)
uv run --with pytest pytest --cov=src/lazy_kafka --cov-report=term

# Generate HTML coverage report
uv run --with pytest pytest --cov=src/lazy_kafka --cov-report=html
# Open in browser: open htmlcov/index.html

# Generate XML coverage report (for CI/CD)
uv run --with pytest pytest --cov=src/lazy_kafka --cov-report=xml
```

### Test Markers

```bash
# Run only unit tests
uv run --with pytest pytest -m unit

# Run only integration tests
uv run --with pytest pytest -m integration

# Run only slow tests
uv run --with pytest pytest -m slow

# Skip slow tests
uv run --with pytest pytest -m "not slow"
```

---

## ✍️ Writing Tests

### Unit Tests

Unit tests test individual functions or classes in isolation, using mocks for dependencies.

**Example: Testing configuration loading**

```python
"""tests/unit/test_config.py"""
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import tomllib

from lazy_kafka.config import Configuration, KafkaConfiguration


class TestConfiguration:
    """Tests for Configuration class."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = Configuration()
        assert config.kafka.bootstrap_servers == "localhost:9092"
        assert config.kafka.group_id == "my-work-group"
        assert config.request_time_out == 1000

    def test_from_toml(self):
        """Test loading configuration from TOML file."""
        toml_content = """
[kafka]
bootstrap_servers = "test-server:9092"
group_id = "test-group"

[registry]
host = "http://test-registry:8081"

[connect]
host = "http://test-connect:8083"
"""
        with NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            
            config = Configuration.from_toml(Path(f.name))
            assert config.kafka.bootstrap_servers == "test-server:9092"
            assert config.registry.host == "http://test-registry:8081"

    def test_kafka_config_to_config(self):
        """Test KafkaConfiguration.to_config() method."""
        kafka_config = KafkaConfiguration(
            bootstrap_servers="localhost:9092",
            group_id="test-group",
        )
        result = kafka_config.to_config()
        
        assert result["bootstrap.servers"] == "localhost:9092"
        assert result["group.id"] == "test-group"
```

### Integration Tests

Integration tests test how components work together, with minimal mocking.

**Example: Testing CLI commands**

```python
"""tests/integration/test_cli.py"""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from typer.testing import CliRunner

from lazy_kafka.cli import app


@pytest.fixture
def runner():
    """Create a Typer test runner."""
    return CliRunner()


@pytest.fixture
def temp_config():
    """Create a temporary config file."""
    with TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / ".lazy-kafka.toml"
        config_path.write_text("""
[kafka]
bootstrap_servers = "localhost:9092"
""")
        yield config_path


class TestCLI:
    """Tests for CLI commands."""

    def test_version(self, runner):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "LazyKafka CLI version" in result.stdout

    def test_config_file_option(self, runner, temp_config):
        """Test --config-file option."""
        result = runner.invoke(app, ["--config-file", str(temp_config)])
        assert result.exit_code == 0
```

### Fixtures

Use pytest fixtures for shared test dependencies.

**Example: Mock Kafka client fixture**

```python
"""tests/conftest.py"""
from unittest.mock import MagicMock, patch

import pytest

from lazy_kafka.config import Configuration, KafkaConfiguration
from lazy_kafka.topic import KafkaClient


@pytest.fixture
def mock_kafka_config():
    """Create a mock Kafka configuration."""
    return KafkaConfiguration(
        bootstrap_servers="localhost:9092",
        group_id="test-group",
    )


@pytest.fixture
def mock_kafka_client(mock_kafka_config):
    """Create a mock Kafka client."""
    with patch("lazy_kafka.topic.Consumer") as mock_consumer_class:
        mock_consumer = MagicMock()
        mock_consumer_class.return_value = mock_consumer
        
        # Mock admin client
        with patch("lazy_kafka.topic.AdminClient") as mock_admin_class:
            mock_admin = MagicMock()
            mock_topic_metadata = MagicMock()
            mock_topic_metadata.topic = "test-topic"
            mock_admin.list_topics.return_value = MagicMock(
                topics={"test-topic": mock_topic_metadata}
            )
            mock_admin_class.return_value = mock_admin
            
            client = KafkaClient(mock_kafka_config)
            yield client


@pytest.fixture
def sample_config_file(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / ".lazy-kafka.toml"
    config_path.write_text("""
[kafka]
bootstrap_servers = "localhost:9092"
group_id = "test-group"

[registry]
host = "http://localhost:8081"

[connect]
host = "http://localhost:8083"
""")
    return config_path
```

---

## 🏷️ Test Types

### Unit Tests

- **Purpose**: Test individual functions/classes in isolation
- **Location**: `tests/unit/`
- **Characteristics**: Fast, isolated, use mocks
- **Marker**: `@pytest.mark.unit`

**Test:**
- Pure functions
- Individual class methods
- Error handling
- Edge cases

### Integration Tests

- **Purpose**: Test component interactions
- **Location**: `tests/integration/`
- **Characteristics**: Use real dependencies where possible, minimal mocking
- **Marker**: `@pytest.mark.integration`

**Test:**
- Plugin system integration
- CLI command workflows
- TUI widget interactions
- API client interactions

### End-to-End Tests

- **Purpose**: Test complete user workflows
- **Location**: `tests/e2e/`
- **Characteristics**: Use test containers or external services, slow
- **Marker**: `@pytest.mark.e2e` and `@pytest.mark.slow`

**Test:**
- Complete message consume/produce flow
- Multi-plugin interactions
- Full application lifecycle

---

## 🎭 Mocking Strategies

### Mocking Kafka Dependencies

The `confluent-kafka` library is a C extension and difficult to mock directly. Use `unittest.mock`:

```python
from unittest.mock import MagicMock, patch

# Mock the Consumer class
with patch("lazy_kafka.topic.Consumer") as mock_consumer_class:
    mock_consumer = MagicMock()
    mock_consumer_class.return_value = mock_consumer
    
    # Use the client
    client = KafkaClient(config)
    # mock_consumer will be used instead of real Consumer
```

### Mocking HTTP Requests

For testing `registry.py` and `connect.py`:

```python
from unittest.mock import patch
import httpx
import pytest

# Using pytest-httpx (recommended)
@pytest.mark.asyncio
async def test_schema_registry_list_subjects():
    """Test SchemaRegistry.list_subjects with mocked HTTP."""
    from lazy_kafka.registry import SchemaRegistry
    
    # Mock response
    mock_response = httpx.Response(
        status_code=200,
        json=["test-subject-1", "test-subject-2"]
    )
    
    # Patch httpx.AsyncClient.get
    with patch.object(httpx.AsyncClient, "get", return_value=mock_response):
        registry = SchemaRegistry(config)
        subjects = await registry.list_subjects()
        assert subjects == ["test-subject-1", "test-subject-2"]
```

### Mocking Textual Widgets

For testing TUI components:

```python
from textual.app import App
from textual.widgets import DataTable

# Use Textual's testing utilities
async def test_topic_panel():
    """Test TopicPanel widget."""
    from lazy_kafka.widgets.topic import TopicPanel
    
    # Create a test app
    app = App()
    
    # Mount the panel
    panel = TopicPanel(mock_hook)
    await app.mount(panel)
    
    # Test panel behavior
    assert panel.BORDER_TITLE == "Topics"
```

---

## 📊 Coverage

### Coverage Configuration

Coverage is configured in `pyproject.toml`:

```toml
[tool.coverage.run]
source_pkgs = ["lazy_kafka", "tests"]
branch = true
parallel = true
omit = [
    "src/lazy_kafka/__about__.py",
]

[tool.coverage.report]
exclude_lines = [
    "no cov",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### Coverage Targets

| Phase | Target Coverage |
|-------|-----------------|
| v0.1.1 | 70% |
| v0.1.2 | 75% |
| v0.1.3 | 80% |
| v0.2.0 | 85% |
| v0.2.1+ | 85% |
| v0.3.0 | 88% |
| v1.0.0 | 90% |

### Checking Coverage Locally

```bash
# Run tests with coverage
uv run --with pytest pytest --cov=src/lazy_kafka --cov-report=term-missing

# Generate HTML report
uv run --with pytest pytest --cov=src/lazy_kafka --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Badge

Add this to your README to show coverage status:

```markdown
![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen)
```

Update the percentage manually or use a service like Codecov or Coveralls.

---

## 💡 Best Practices

### 1. Test Naming

Use descriptive test names:

```python
# Good
def test_configuration_from_toml_loads_kafka_settings():
    """Test that Configuration.from_toml loads Kafka settings correctly."""
    
# Bad (too vague)
def test_config():
    pass
```

### 2. Test Isolation

Each test should be independent:

```python
# Good: Each test creates its own data
def test_create_topic():
    topic = Topic("test-topic")
    # Test with this topic

def test_list_topics():
    topics = [Topic("topic-1"), Topic("topic-2")]
    # Test with these topics
    
# Bad: Tests depend on each other
test_topic = None

def test_create():
    global test_topic
    test_topic = Topic("test")

def test_use():
    # Depends on test_create running first
    assert test_topic is not None
```

### 3. Use Fixtures for Common Setup

```python
# Good: Use fixture for shared setup
@pytest.fixture
def mock_client():
    return KafkaClient(MagicMock())

def test_client_list_topics(mock_client):
    # Use mock_client
    
# Bad: Duplicate setup
class TestClient:
    def setup_method(self):
        self.client = KafkaClient(MagicMock())
    
    def test_one(self):
        # Use self.client
        
    def test_two(self):
        # Use self.client (setup duplicated)
```

### 4. Test Edge Cases

```python
# Good: Test edge cases
def test_parse_message_with_none_value():
    """Test parsing a message with None value."""
    
def test_parse_message_with_empty_string():
    """Test parsing a message with empty string."""
    
def test_parse_message_with_malformed_json():
    """Test parsing a message with malformed JSON."""
    
# Bad: Only test happy path
def test_parse_message():
    # Only tests valid JSON
    pass
```

### 5. Use Assertions Effectively

```python
# Good: Specific assertions
def test_list_topics():
    topics = client.list_topics()
    assert len(topics) == 3
    assert "test-topic" in topics
    assert all(isinstance(t, Topic) for t in topics)
    
# Bad: Vague assertions
def test_list_topics():
    topics = client.list_topics()
    assert topics  # Just checks it's truthy
```

### 6. Parameterized Tests

Use `@pytest.mark.parametrize` for testing multiple inputs:

```python
@pytest.mark.parametrize("bootstrap_servers,expected", [
    ("localhost:9092", "localhost:9092"),
    ("kafka:9092,kafka2:9092", "kafka:9092,kafka2:9092"),
    ("", "localhost:9092"),  # Default
])
def test_bootstrap_servers_config(bootstrap_servers, expected):
    """Test bootstrap.servers configuration."""
    config = KafkaConfiguration(bootstrap_servers=bootstrap_servers or None)
    result = config.to_config()["bootstrap.servers"]
    assert result == expected
```

### 7. Mark Slow Tests

Mark tests that take a long time to run:

```python
@pytest.mark.slow
@pytest.mark.asyncio
async def test_large_message_set():
    """Test with large number of messages (slow)."""
    # This test takes a while
    pass
```

### 8. Skip Tests When Appropriate

```python
@pytest.mark.skip(reason="Feature not yet implemented")
def test_produce_messages():
    pass

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Not supported on Windows"
)
def test_unix_socket():
    pass
```

---

## 🔧 Test Configuration

### pytest Configuration

Create a `pytest.ini` or `pyproject.toml` section:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Tests that take a long time",
]
```

### Pre-commit Hooks

Tests run automatically on commit via pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  - repo: local
    hooks:
      - id: pytest
        name: Run tests
        entry: uv run --with pytest pytest
        language: system
        types: [python]
        pass_filenames: false
```

---

## 🚀 CI/CD Integration

### GitHub Actions

Tests run automatically in CI via `.github/workflows/build.yaml`:

```yaml
- name: Run tests
  run: |
    set +e
    uv run --with pytest pytest -q
    code=$?
    set -e
    if [ "$code" -eq 5 ]; then
      echo "::notice::No tests collected yet - add tests under tests/."
      exit 0
    fi
    exit "$code"
```

### Nightly Builds

Nightly builds run tests with coverage in `.github/workflows/nightly-build.yaml`:

```yaml
- name: Run tests with coverage
  run: |
    uv run --with pytest pytest -q --cov=src/lazy_kafka --cov-report=xml --cov-report=html
```

---

## 📚 Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest Markers](https://docs.pytest.org/en/stable/mark.html)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-httpx](https://pytest-httpx.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 🎯 Test Checklist

Before submitting a PR:

- [ ] All new code has corresponding tests
- [ ] Existing tests still pass
- [ ] Tests cover edge cases
- [ ] Tests are properly named and organized
- [ ] Test coverage is maintained or increased
- [ ] Tests run in a reasonable time (< 1 minute for unit tests)
- [ ] Slow tests are marked with `@pytest.mark.slow`

---

*Last updated: 2026-08-30*
