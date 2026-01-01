"""Pytest configuration for all tests."""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests (tests that use real time.sleep)",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Modify pytest configuration based on options."""
    if config.getoption("--run-slow"):
        # Override the default marker expression to include slow tests
        # This removes 'not slow' from the filter while keeping other filters
        current = config.option.markexpr
        if current:
            # Remove 'not slow' and 'and not slow' from expression
            new_expr = current.replace(" and not slow", "").replace("not slow", "")
            # Clean up any leading/trailing 'and'
            new_expr = new_expr.strip()
            if new_expr.startswith("and "):
                new_expr = new_expr[4:]
            if new_expr.endswith(" and"):
                new_expr = new_expr[:-4]
            # Handle empty expression
            if not new_expr or new_expr == "and":
                new_expr = ""
            config.option.markexpr = new_expr
