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

### API Documentation
- **V2 API** (current): https://jpx-jquants.com/ja/spec/
  - プラン別エンドポイント一覧: https://jpx-jquants.com/ja/spec/data-spec

## Documentation Map (Progressive Disclosure)

Start here and follow links only as needed.

- `README.md`: End-user quickstart (install/config/basic usage).
- `docs/design/v2/README.md`: Contributor/agent index for ClientV2 design.
  - Read when: adding/changing endpoints, error handling, pagination, rate limiting, DataFrame contracts.

## Package Structure

```
jquants/             # V2 client
├── client_v2.py     # ClientV2 with API key auth
├── constants_v2.py  # V2 column definitions
├── exceptions.py    # Custom exceptions
└── pacer.py         # Rate limiting
```

## Client Pattern

```python
# Each endpoint follows this pattern:
_get_*_raw()      # Raw JSON, handles pagination
get_*()           # Returns sorted DataFrame
get_*_range()     # Date range with ThreadPoolExecutor(max_workers=5)
```

## Code Style

- Python 3.12+
- Black formatter, isort
- flake8 max-line-length=120
- mypy type checking
