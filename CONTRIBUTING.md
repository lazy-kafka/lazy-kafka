# Contributing to Lazy-Kafka

Thank you for your interest in contributing to lazy-kafka! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Pull Request Guidelines](#-pull-request-guidelines)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Labeling Issues](#-labeling-issues)
- [Code Review Process](#-code-review-process)
- [Release Process](#-release-process)

---

## 🤝 Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or 3.12
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [GitHub CLI](https://cli.github.com/) (for milestone/issue management)
- Docker and Docker Compose (for local Kafka environment)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Timon Viola/lazy-kafka.git
cd lazy-kafka

# Install development dependencies with uv
uv sync --locked

# Or with pip
pip install -e ".[dev]"
```

---

## 💻 Development Setup

### Local Development Environment

#### Using uv (Recommended)

```bash
# Install the package in development mode
uv sync --locked

# Install pre-commit hooks
uv run pre-commit install --hook-type commit-msg

# Run the TUI
uv run textual run --dev src/lazy_kafka/__main__.py

# Run the CLI
uv run python -m lazy_kafka --help
```

#### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install --hook-type commit-msg
```

### Docker Environment

The project includes a Docker Compose setup for a complete Kafka ecosystem:

```bash
# Start all services (Kafka, Zookeeper, Schema Registry, Kafka Connect)
./scripts/start-up

# Initialize test data
./scripts/create_schema.sh
./scripts/create_connector.sh
./scripts/init-aws.sh
```

Services will be available at:
- Kafka: `localhost:9092`
- Zookeeper: `localhost:2181`
- Schema Registry: `localhost:8081`
- Kafka Connect: `localhost:8083`
- LocalStack (S3/SQS): `localhost:4566`

---

## 📝 Pull Request Guidelines

### Before Submitting a PR

1. **Fork the repository** and create a branch from `trunk`
   ```bash
   git checkout trunk
   git pull origin trunk
   git checkout -b feature/your-feature-name
   ```

2. **Ensure your changes are focused** - One feature or bug fix per PR

3. **Update documentation** - If your change affects the API or behavior, update relevant docs

4. **Add tests** - New features must include tests

5. **Run the following checks locally**:
   ```bash
   # Linting
   uv run ruff check
   
   # Formatting
   uv run ruff format
   
   # Type checking
   uv run mypy --install-types --non-interactive src/lazy_kafka tests
   
   # Tests
   uv run --with pytest pytest
   ```

### PR Requirements

- [ ] **Title**: Clear and descriptive
- [ ] **Description**: Explain what the PR does and why
- [ ] **Linked to issue**: Reference the issue number in the PR description
- [ ] **Linked to milestone**: Assign the PR to the appropriate milestone
- [ ] **All tests pass**: CI must be green
- [ ] **Coverage maintained**: Test coverage should not decrease
- [ ] **Code formatted**: ruff format must pass
- [ ] **Type checking passes**: mypy must pass
- [ ] **Documentation updated**: If applicable
- [ ] **Changelog entry**: Add a news fragment (see below)

### PR Title Format

Use one of these prefixes:
- `feat: ` - New feature
- `fix: ` - Bug fix
- `docs: ` - Documentation changes
- `test: ` - Test changes
- `refactor: ` - Code refactoring
- `chore: ` - Maintenance tasks
- `ci: ` - CI/CD changes

Examples:
- `feat: add message filtering in TUI`
- `fix: handle None messages in consumer`
- `docs: update README with usage examples`
- `test: add unit tests for config module`

---

## 🧪 Testing

See [TESTING.md](TESTING.md) for detailed testing guidelines.

### Quick Test Commands

```bash
# Run all tests
uv run --with pytest pytest

# Run tests with coverage
uv run --with pytest pytest --cov=src/lazy_kafka --cov-report=term-missing

# Run a specific test file
uv run --with pytest pytest tests/test_module.py

# Run tests with verbose output
uv run --with pytest pytest -v

# Run only unit tests
uv run --with pytest pytest -m unit

# Run only integration tests
uv run --with pytest pytest -m integration
```

---

## 📚 Documentation

### Documentation Structure

| Document | Purpose |
|----------|---------|
| README.md | Project overview, installation, usage |
| ROADMAP.md | Development roadmap and milestones |
| CONTRIBUTING.md | This document |
| TESTING.md | Testing guidelines |
| .github/ROADMAP_SETUP.md | CI/CD and milestone setup guide |

### Updating Documentation

When contributing documentation:
1. Use consistent formatting and style
2. Keep examples up to date
3. Test code snippets when possible
4. Use relative links for internal references

---

## 🏷️ Labeling Issues

### Issue Labels

Please use the following labels when creating or triaging issues:

| Label | When to Use |
|-------|-------------|
| `bug` | Bug reports |
| `enhancement` | Feature requests |
| `documentation` | Documentation improvements |
| `test` | Test-related tasks |
| `priority:high` | Critical issues, blocking next release |
| `priority:medium` | Important but not blocking |
| `priority:low` | Nice to have, backlog |
| `kafka` | Kafka-related issues |
| `connect` | Kafka Connect-related issues |
| `registry` | Schema Registry-related issues |
| `tui` | Textual TUI issues |
| `cli` | Command-line interface issues |
| `good first issue` | Good for new contributors |
| `help wanted` | Needs community help |

### Label Combinations

Common label combinations:
- `bug, priority:high, kafka` - Critical Kafka bug
- `enhancement, priority:medium, tui` - TUI feature request
- `test, priority:high` - Test infrastructure issue
- `documentation, priority:low` - Documentation improvement

---

## 👀 Code Review Process

### For Contributors

1. **Submit your PR** following the guidelines above
2. **Wait for review** - Maintainers will review within a few days
3. **Address feedback** - Make requested changes and push new commits
4. **Rebase if needed** - Keep your PR up to date with trunk
5. **Wait for approval** - At least one maintainer must approve

### For Reviewers

1. **Acknowledge the PR** - Comment to let the author know you're reviewing
2. **Check the checklist**:
   - [ ] Title and description are clear
   - [ ] Code follows project conventions
   - [ ] Tests are added/updated
   - [ ] Documentation is updated (if needed)
   - [ ] Changelog entry is added
   - [ ] All CI checks pass
3. **Provide feedback**:
   - Be constructive and specific
   - Suggest improvements, not just point out problems
   - Use GitHub's suggestion feature for small changes
4. **Approve or request changes**

### Review Criteria

✅ **Functionality**: Does it work as intended?
✅ **Code Quality**: Is it clean, readable, and maintainable?
✅ **Tests**: Are there sufficient tests?
✅ **Documentation**: Is it documented?
✅ **Compatibility**: Does it break existing functionality?
✅ **Performance**: Are there performance implications?

---

## 🚀 Release Process

### Versioning

Lazy-Kafka follows [Semantic Versioning](https://semver.org/):
- `MAJOR` - Breaking changes
- `MINOR` - New features (backwards compatible)
- `PATCH` - Bug fixes (backwards compatible)

Pre-release versions use suffixes:
- `-alpha.N` - Alpha releases
- `-beta.N` - Beta releases
- `-rc.N` - Release candidates

### Creating a Release

#### 1. Prepare the Release

```bash
# Update version in pyproject.toml if needed
# The project uses versioningit, so version is derived from git tags

# Update ROADMAP.md with completion status
# Update CHANGELOG (or add news fragments for towncrier)

# Run all tests
uv run --with pytest pytest --cov=src/lazy_kafka

# Verify build
uv build
```

#### 2. Create Release Tag

```bash
# For stable release
git tag v1.0.0

# For pre-release
git tag v1.0.0-rc1

# Push tag
git push origin v1.0.0
```

The CI/CD workflow will automatically:
1. Build the distribution
2. Run tests
3. Create a GitHub Release
4. Publish to PyPI (stable releases only)
5. Publish to TestPyPI (pre-releases only)

#### 3. Post-Release

```bash
# Update milestone status
gh api repos/Timon Viola/lazy-kafka/milestones -X PATCH \
  -f title=v1.0.0 -f state=closed

# Create next milestone
gh api repos/Timon Viola/lazy-kafka/milestones -X POST \
  -f title=v1.1.0 -f description="Next release" -f due_on="2027-03-01T23:59:59Z"

# Announce release
# Post in discussions, social media, etc.
```

### Manual Release (Alternative)

```bash
# Create and push tag manually
git tag v1.0.0
 git push origin v1.0.0

# Or trigger workflow manually
gh workflow run release.yaml --field version=v1.0.0
```

---

## 📝 Changelog

### Using Towncrier

The project uses [Towncrier](https://towncrier.readthedocs.io/) for changelog management.

#### Adding a Changelog Entry

Create a news fragment file in the appropriate directory:

```bash
# For a new feature
mkdir -p doc/changes/feature
vi doc/changes/feature/your-feature.123.rst

# For a bug fix
mkdir -p doc/changes/bugfix
vi doc/changes/bugfix/your-fix.456.rst

# For a documentation change
mkdir -p doc/changes/doc
vi doc/changes/doc/your-doc-change.789.rst
```

Fragment format (RST):
```rst
Add message filtering functionality in TUI.
```

#### Building the Changelog

```bash
# Generate changelog
uv run towncrier build --yes

# Commit the changes
 git add doc/changelog.rst
git commit -m "docs: update changelog"
```

### Changelog Categories

| Category | Directory | Purpose |
|----------|-----------|---------|
| `feature` | `doc/changes/feature/` | New features |
| `bugfix` | `doc/changes/bugfix/` | Bug fixes |
| `doc` | `doc/changes/doc/` | Documentation changes |
| `removal` | `doc/changes/removal/` | Deprecations and removals |
| `deprecation` | `doc/changes/deprecation/` | Deprecation warnings |
| `misc` | `doc/changes/misc/` | Miscellaneous changes |

---

## 🛠 Project Structure

```
lazy-kafka/
├── pyproject.toml           # Project configuration
├── README.md                # Project documentation
├── ROADMAP.md               # Development roadmap
├── CONTRIBUTING.md          # This file
├── TESTING.md               # Testing guidelines
├── CODE_OF_CONDUCT.md       # Code of conduct
├── src/
│   └── lazy_kafka/
│       ├── __init__.py      # Package exports
│       ├── __main__.py      # TUI/CLI entry point
│       ├── __about__.py     # Version info
│       ├── config.py        # Configuration handling
│       ├── topic.py         # Kafka client
│       ├── registry.py      # Schema Registry client
│       ├── connect.py       # Kafka Connect client
│       ├── cli/             # CLI commands
│       ├── plugin/          # Plugin system
│       ├── plugins/         # Built-in plugins
│       └── widgets/         # Textual widgets
├── tests/                   # Tests
├── scripts/                 # Utility scripts
├── .github/
│   ├── workflows/          # GitHub Actions workflows
│   └── ROADMAP_SETUP.md    # CI/CD setup guide
└── doc/                    # Documentation
    ├── changelog.rst       # Generated changelog
    └── changes/            # Towncrier news fragments
```

---

## 🎯 Getting Help

### Asking Questions

- Check the [README](README.md) first
- Look at existing [issues](https://github.com/Timon Viola/lazy-kafka/issues)
- Search [discussions](https://github.com/Timon Viola/lazy-kafka/discussions)
- Create a new discussion for general questions

### Reporting Issues

When reporting a bug:
1. **Check if it's already reported** - Search existing issues
2. **Provide details**:
   - Python version
   - Operating system
   - Lazy-Kafka version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages (full traceback)
3. **Use the bug report template**

---

## 🙏 Acknowledgments

Thank you to all contributors who have helped make lazy-kafka better!

---

*Last updated: 2026-08-30*
