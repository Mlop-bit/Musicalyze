test:
    cd services/ml && uv run --frozen pytest

test-live:
    cd services/ml && uv run --frozen pytest -m live

lint:
    cd services/ml && uv run --frozen ruff check . && uv run --frozen ruff format --check .

typecheck:
    cd services/ml && uv run --frozen pyright

check: lint typecheck test

sync:
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
        cd services/ml && uv sync --extra cu130
    else
        cd services/ml && uv sync --extra cpu
    fi

sync-cpu:
    cd services/ml && uv sync --extra cpu

sync-gpu:
    cd services/ml && uv sync --extra cu130

docker-build:
    docker build -t musicalyze-ml services/ml

migrate:
    cd services/ml && uv run alembic upgrade head

migration message:
    cd services/ml && uv run alembic revision --autogenerate -m "{{message}}"

install-hooks:
    cd services/ml && uv run pre-commit install
