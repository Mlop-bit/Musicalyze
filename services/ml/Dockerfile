FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev --extra cpu
COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations
RUN uv sync --frozen --no-dev --extra cpu
EXPOSE 8000
CMD ["uv", "run", "--frozen", "--no-dev", "--extra", "cpu", "uvicorn", "ml.serving.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
