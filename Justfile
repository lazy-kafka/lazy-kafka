set shell := ["bash", "-euo", "pipefail", "-c"]

# One-stop local dev setup (install pre-commit hooks, etc.). Run once after cloning.
setup:
    uv run pre-commit install --hook-type commit-msg

# Run the test suite with coverage
test *args:
    uv run pytest --cov=lazy_kafka --cov-report=term-missing --cov-report=xml --cov-report=html tests {{args}}

# Bump version + changelog locally (mirrors .github/workflows/release.yaml).
# increment: auto | patch | minor | major
release increment="auto":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "{{increment}}" = "auto" ]; then
      cog bump --auto --changelog
    else
      cog bump --increment "{{increment}}" --changelog
    fi
