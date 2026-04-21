DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_FILE = docker-compose.yml

.PHONY: help up down restart logs clean setup run cache migrate makemigration test coverage test-matching lintfix

help:
	@echo "Available commands:"
	@echo "  make makemigration desc='msg'     - Create new migration"
	@echo "  make migrate                      - Apply all migrations"
	@echo "  make up                           - Start services"
	@echo "  make down                         - Stop services"
	@echo "  make restart                      - Restart services"
	@echo "  make logs                         - Show logs"
	@echo "  make clean                        - Remove unused Docker data"
	@echo "  make setup                        - Setup project (venv, deps, pre-commit, migrations)"
	@echo "  make run                          - Run FastAPI with uvicorn"
	@echo "  make cache                        - Remove all cached files"
	@echo "  make test                         - Run all tests"
	@echo "  make test-matching N=pattern      - Run tests matching name pattern"
	@echo "  make coverage                     - Run all tests with coverage"
	@echo "  make lintfix                      - Run pre-commit run for all files"


# Docker
up:
	@echo "Starting services..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d

down:
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

restart: down up

logs:
	@echo "Showing logs..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

clean:
	@echo "Cleaning up..."
	docker system prune -a --volumes -f


# Set up
env:
	@if [ ! -f .env ]; then \
		cp .example.env .env && echo ".env created"; \
	else \
		sort .example.env > .example.env.sorted; \
		sort .env > .env.sorted; \
		MISSING=$$(comm -23 .example.env.sorted .env.sorted); \
		rm .example.env.sorted .env.sorted; \
		if [ -z "$$MISSING" ]; then \
			echo "Everything up to date or .env is ahead (unchanged)"; \
		else \
			cp .example.env .env && echo ".env updated"; \
		fi; \
	fi

setup:
	@echo "Setting up project..."
	@uv sync
	@uv run pre-commit install
	@$(MAKE) -s migrate
	@echo "Setup Completed."


# App
run:
	uv run python -m app.main
runt:
	uv run opentelemetry-instrument python -m app.main


# Utils
cache:
	@echo "Cleaning all cached files..."
	@find . \( -name *.py[co] -o -name __pycache__ \) -delete
	@rm -rf .ruff_cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@echo "Done."


# database migrations
migrate:
	@PYTHONPATH=$PYTHONPATH:$(pwd) uv run alembic upgrade head

makemigration:
	@PYTHONPATH=$PYTHONPATH:$(pwd) uv run alembic revision --autogenerate -m $(desc)


# Tests
test:
	@uv run pytest

coverage:
	@uv run pytest --cov=app --cov-report=term-missing --cov-report=html
	@rm -f .coverage
	@xdg-open htmlcov/index.html # if you want to open in the browser automatically

test-matching:
	@uv run pytest -vv -k $(N)


# Code formating
lintfix:
	@uv run pre-commit run --all-files


# Internacionalization and Localization
i18n-extract:
	uv run pybabel extract -F app/core/i18n/babel.cfg -o app/core/i18n/locales/messages.pot app

i18n-update:
	uv run pybabel update -i app/core/i18n/locales/messages.pot -d app/core/i18n/locales

i18n-compile:
	uv run pybabel compile -d app/core/i18n/locales

# Observability
otel-instrument: # dev env
	uv run --group otel python -m ensurepip --upgrade
	uv run --group otel opentelemetry-bootstrap -a install
