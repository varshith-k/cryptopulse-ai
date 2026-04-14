PROJECT_NAME=cryptopulse-ai

.PHONY: help up down logs api frontend test lint format init-db

help:
	@echo "Available targets:"
	@echo "  make up        - Start the local platform"
	@echo "  make down      - Stop the local platform"
	@echo "  make logs      - Stream Docker Compose logs"
	@echo "  make api       - Run the API locally"
	@echo "  make frontend  - Run the frontend locally"
	@echo "  make test      - Run backend tests"
	@echo "  make lint      - Run backend lint checks"
	@echo "  make format    - Format backend code"

up:
	docker compose up --build

down:
	docker compose down --remove-orphans

logs:
	docker compose logs -f

api:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd apps/frontend && npm run dev -- --host 0.0.0.0 --port 5173

test:
	cd apps/api && pytest

lint:
	cd apps/api && ruff check .

format:
	cd apps/api && ruff format .

