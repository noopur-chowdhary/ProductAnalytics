.PHONY: install test lint api docker-up docker-down features train-rr train-or train-uplift decisions

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check src api scripts tests

api:
	uvicorn api.main:app --reload --port 8000

features:
	python scripts/build_features.py --dataset all

train-rr:
	python scripts/train_propensity.py --dataset retailrocket

train-or:
	python scripts/train_propensity.py --dataset online_retail

train-uplift:
	python scripts/train_uplift.py

decisions:
	python scripts/build_decisions.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down
