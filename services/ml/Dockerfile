FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-default-groups --extra cpu
COPY src ./src
RUN uv sync --frozen --no-default-groups --no-editable --extra cpu

FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN useradd --create-home app && chown app /app
COPY --from=builder /app/.venv ./.venv
COPY alembic.ini ./
COPY migrations ./migrations
USER app
EXPOSE 8000
CMD ["uvicorn", "ml.serving.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
