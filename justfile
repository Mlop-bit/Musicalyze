test:
    cd services/ml && uv run --frozen pytest

lint:
    cd services/ml && uv run --frozen ruff check . && uv run --frozen ruff format --check .

typecheck:
    cd services/ml && uv run --frozen pyright

check: lint typecheck test

sync:
    cd services/ml && uv sync --extra cpu

sync-gpu:
    cd services/ml && uv sync --extra cu130

docker-build:
    docker build -t musicalyze-ml services/ml

install-hooks:
    cd services/ml && uv run pre-commit install
