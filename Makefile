.PHONY: dev lint format test

# Backend
dev:
	cd backend && uv run uvicorn src.main:app --reload

lint:
	cd backend && uv run ruff check .

format:
	cd backend && uv run ruff format .

test:
	cd backend && uv run pytest $(filter-out $@,$(MAKECMDGOALS))

%:
	@:
