
.PHONY: lint
lint:
	poetry run isort .
	poetry run black . --check
	poetry run flake8 -j 1 .
	poetry run mypy .

.PHONY: lint-fix
lint-fix:
	poetry run isort .
	poetry run black .
	poetry run flake8 -j 1 .
	poetry run mypy .

.PHONY: test
test:
	poetry run pytest --cov=./jquants tests/

.PHONY: test-integration
test-integration:
	poetry run pytest -m integration tests/

.PHONY: test-all
test-all:
	poetry run pytest -m "" --cov=./jquants tests/
