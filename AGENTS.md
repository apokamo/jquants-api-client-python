# AGENTS.md

Project instructions for AI coding agents.

## Boundaries

### 🚫 Never do
- Push, PR, or issue to `J-Quants/jquants-api-client-python` (upstream/official)
- Run `gh` commands without verifying target repo first
- Modify files without running lint

### ✅ Always do
- Target `apokamo/jquants-api-client-python` (our fork) for all git/gh operations
- Verify with `gh repo view --json nameWithOwner` before any `gh` command
- Run `make lint` before committing

### ⚠️ Ask first
- Changes to public API signatures
- New dependencies in pyproject.toml

## Commands

```bash
# Setup (local .venv with Poetry)
uv venv --python /usr/bin/python3 --seed .venv
uv pip install --python .venv/bin/python poetry
export POETRY_CACHE_DIR="$PWD/.poetry-cache"
.venv/bin/poetry config virtualenvs.in-project true --local
.venv/bin/poetry install

# Test
.venv/bin/poetry run make test

# Lint (check)
.venv/bin/poetry run make lint

# Lint (fix)
.venv/bin/poetry run make lint-fix
```

## Git Remotes

```
origin   → apokamo/jquants-api-client-python (push here)
upstream → J-Quants/jquants-api-client-python (pull only, NEVER push)
```

## Project Overview

J-Quants API Python client library for Japanese stock market data (JPX).
API docs: https://jpx.gitbook.io/j-quants-ja/

## Package Structure

```
jquantsapi/          # V1 client (deprecated)
├── client.py        # Client class with all API methods
├── constants.py     # DataFrame column definitions
└── enums.py         # MARKET_API_SECTIONS etc.

jquants/             # V2 client (in development)
├── client_v2.py     # ClientV2 with API key auth
├── constants_v2.py  # V2 column definitions
└── exceptions.py    # Custom exceptions
```

## Client Pattern

```python
# Each endpoint follows this pattern:
_get_*_raw()      # Raw JSON, handles pagination
get_*()           # Returns sorted DataFrame
get_*_range()     # Date range with ThreadPoolExecutor(max_workers=5)
```

## Code Style

- Python 3.8+ (tomli for <3.11, tomllib for 3.11+)
- Black formatter, isort
- flake8 max-line-length=120
- mypy type checking
