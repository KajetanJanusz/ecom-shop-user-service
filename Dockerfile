FROM python:3.14.0-slim-bookworm AS base

ARG POETRY_VERSION=2.3.2

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=${POETRY_VERSION}

RUN pip install poetry==${POETRY_VERSION}


FROM base AS build-stage

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-root --only main

COPY . .

RUN poetry build


FROM python:3.14.0-slim-bookworm AS prod-stage

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

RUN groupadd -g 1001 appgroup && \
    useradd -m -u 1001 -g appgroup appuser

WORKDIR /app

COPY --from=build-stage /app/dist/*.whl .

RUN pip install *.whl

USER appuser


FROM base AS dev-stage

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-root

COPY . .




