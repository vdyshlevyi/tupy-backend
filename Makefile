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

setup: venv/bin/activate ## Project setup
	venv/bin/pip install --upgrade pip
	venv/bin/pip install poetry
	venv/bin/poetry install


run: venv/bin/activate ## Run project
	venv/bin/python entry.py


lint: venv/bin/activate ## Run linter
	venv/bin/ruff format --config ./pyproject.toml . && venv/bin/ruff check --fix --config ./pyproject.toml .

mypy: venv/bin/activate ## Run mypy
	venv/bin/mypy ./

coverage: venv/bin/activate ## Run tests coverage
	venv/bin/coverage run --source="app" --omit=*/__init__.py -m pytest -vv
	venv/bin/coverage xml
	venv/bin/coverage report -m --fail-under=80.00



# Just help
help: ## Display help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
