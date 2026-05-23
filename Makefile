.PHONY: help dev-infra backend frontend lint test clean

help:
	@echo "Available commands:"
	@echo "  make dev-infra   - Start PostgreSQL, Redis, RabbitMQ"
	@echo "  make backend     - Start FastAPI dev server"
	@echo "  make frontend    - Start Next.js dev server"
	@echo "  make lint        - Run Python linting"
	@echo "  make test        - Run backend tests"
	@echo "  make clean       - Stop all containers"

dev-infra:
	cd docker && docker compose up -d

backend:
	backend:
	cd backend && .venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

lint:
	cd backend && black app/ && isort app/ && mypy app/

test:
	cd backend && pytest tests/ -v --cov=app

clean:
	cd docker && docker compose down
