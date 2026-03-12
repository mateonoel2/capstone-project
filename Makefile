.PHONY: dev lint format test migrate up down logs

# Backend
dev:
	cd backend && uv run uvicorn src.main:app --reload

lint:
	cd backend && uv run ruff check .

format:
	cd backend && uv run ruff format .

test:
	cd backend && uv run pytest $(filter-out $@,$(MAKECMDGOALS))

migrate:
	cd backend && uv run alembic upgrade head

# Docker
up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

%:
	@:
