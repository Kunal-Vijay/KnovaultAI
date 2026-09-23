install:
	poetry install

run:
	docker-compose up --build

test:
	poetry run pytest

linit:
	poetry run ruff check app tests

format:
	poetry run ruff format app tests

init-db:
	docker-compose exec fastapi_app sh -c "alembic init -t async migrations"
	migrate-db

migrate-db:
	docker-compose exec fastapi_app alembic upgrade head

create-migration:
	docker-compose exec fastapi_app alembic revision --autogenerate -m "$(MESSAGE)"
