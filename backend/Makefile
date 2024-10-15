# Server
.PHONY: runserver
runserver:
	poetry run uvicorn src.main:app --host localhost --reload

# Alembic
.PHONY: migrate
migrate:
	poetry run alembic upgrade head

.PHONY: downgrade
downgrade:
	poetry run alembic downgrade -1 

# Celery
.PHONY: celery_worker
celery_worker:
	poetry run celery -A src.core.celery worker --loglevel=INFO 

.PHONY: celery_beat
celery_beat:
	poetry run celery -A src.core.celery beat --loglevel=INFO

.PHONY: celery_flower
celery_flower:
	poetry run celery -A src.core.celery flower

# Tests
.PHONY: test
test:
	poetry run pytest -s

.PHONY: many_test
many_test:
	for x in {1..5}; do poetry run pytest -s; done

.PHONY: cg
cg:
	poetry run coverage run -m pytest -s

.PHONY: cg_report
cg_report:
	poetry run coverage html
