.PHONY: setup \
		run \
		lint \
		mypy \

		test \
		test-unit \
		test-integration \
		coverage \

		db-current \
		db-downgrade \
		db-history \
		db-revision \
		db-show \
		db-upgrade \

		help

venv/bin/activate: ## Alias for virtual environment
	python -m venv venv
	export POETRY_VIRTUALENVS_PATH=./venv

setup: venv/bin/activate ## Project setup
	. venv/bin/activate; pip install --upgrade pip
	. venv/bin/activate; pip install poetry
	. venv/bin/activate; poetry install


run: ## Run project
	. venv/bin/activate; python entry.py


lint: ## Run linter
	. venv/bin/activate; ruff format --config ./pyproject.toml . && ruff check --fix --config ./pyproject.toml .

mypy: ## Run mypy
	. venv/bin/activate; mypy ./

test: ## Run tests check
	poetry run pytest $(filter-out $@,$(MAKECMDGOALS)) -s

test-unit: ## Run unit tests
	poetry run pytest $(filter-out $@,$(MAKECMDGOALS)) -s -k "unit"

test-integration: ## Run integration tests
	poetry run pytest $(filter-out $@,$(MAKECMDGOALS)) -s -k "integration"

coverage: ## Run tests coverage
	. venv/bin/activate; coverage run --source="app" --omit=*/__init__.py -m pytest -vv
	. venv/bin/activate; coverage xml
	. venv/bin/activate; coverage report -m --fail-under=80.00


# Migration commands
db-upgrade: ## Apply migrations
	. venv/bin/activate; alembic upgrade head
db-current: ## Current migration
	. venv/bin/activate; alembic current
db-revision: ## Create new db revision
	. venv/bin/activate; alembic revision --autogenerate -m "$(filter-out $@,$(MAKECMDGOALS))"
db-show: ## Show migrations
	. venv/bin/activate; alembic show head
db-history: ## Show all migrations
	. venv/bin/activate; alembic history
db-downgrade: ## Downgrade db to -1 migration
	. venv/bin/activate; alembic downgrade -1


# Just help
help: ## Display help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
