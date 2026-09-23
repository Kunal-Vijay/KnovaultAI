install:
	pip install -r requirements-dev.txt

run:
	docker compose up --build

test:
	pytest

lint:
	ruff check app tests

format:
	ruff format app tests

init-db:
	migrate-db

migrate-db:
	docker compose exec fastapi_app alembic upgrade head

create-migration:
	docker compose exec fastapi_app alembic revision --autogenerate -m "$(MESSAGE)"
