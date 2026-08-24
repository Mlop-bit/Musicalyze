test:
    cd services/ml && uv run pytest

lint:
    cd services/ml && uv run ruff check . && uv run ruff format --check .

typecheck:
    cd services/ml && uv run pyright

check: lint typecheck test

sync:
    cd services/ml && uv sync

docker-build:
    docker build -t musicalyze-ml services/ml

install-hooks:
    cd services/ml && uv run pre-commit install
