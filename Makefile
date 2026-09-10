install:
	pip install -r requirements.txt

run-api:
	uvicorn app.api.app:app --reload

run-bot:
	python -m app.bot.main

migrate:
	alembic upgrade head

test:
	pytest -q

docker-up:
	docker compose up --build

docker-down:
	docker compose down
