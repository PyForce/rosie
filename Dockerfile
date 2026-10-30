# syntax=docker/dockerfile:1.7
FROM python:3.15-slim AS builder

# Pin uv; use a digest as well when your deployment requires immutable inputs.
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/

WORKDIR /app
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

# Resolve and install third-party dependencies in a cacheable layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,readonly \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,readonly \
    uv sync --locked --no-dev --no-install-project --no-editable

COPY . /app

# Install the packaged application non-editably for deployment.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app


CMD ["rosie"]

