install:
	pip install -r requirements.txt

run:
	docker compose up --build -d

test:
	pytest

linit:
	ruff check app tests

format:
	ruff format app tests

init-db:
	docker compose exec fastapi_app sh -c "alembic init -t async migrations"
	migrate-db

migrate-db:
	docker compose exec fastapi_app alembic upgrade head

create-migration:
	docker compose exec fastapi_app alembic revision --autogenerate -m "$(MESSAGE)"

run-evals:
	docker compose exec fastapi_app python scripts/run_evals.py run

save-baseline:
	docker compose exec fastapi_app python scripts/run_evals.py save_baseline
