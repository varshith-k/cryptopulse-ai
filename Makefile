PROJECT_NAME=cryptopulse-ai

.PHONY: help up down logs api frontend test lint format frontend-build smoke migrate

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
	@echo "  make frontend-build - Run the frontend production build"
	@echo "  make smoke     - Hit core health and readiness endpoints"
	@echo "  make migrate   - Run Alembic migrations inside the API container"

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

frontend-build:
	cd apps/frontend && npm run build

smoke:
	curl -s http://localhost:8000/health
	curl -s http://localhost:8000/api/v1/system/ready
	curl -s http://localhost:8080/health/ready

migrate:
	docker compose run --rm api alembic upgrade head

lint:
	cd apps/api && ruff check .

format:
	cd apps/api && ruff format .
