FROM python:3.12-alpine as base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BOT_CONFIG_PATH=/data
WORKDIR /app

RUN apk add --no-cache cairo


FROM base as builder

RUN python -m venv /opt/poetry-venv
RUN /opt/poetry-venv/bin/pip install --upgrade pip setuptools
RUN /opt/poetry-venv/bin/pip install poetry

RUN python -m venv .venv

COPY poetry.lock pyproject.toml .
RUN /opt/poetry-venv/bin/poetry install --no-interaction --only main --no-root

COPY . .
RUN /opt/poetry-venv/bin/poetry build --no-interaction --format wheel
RUN .venv/bin/pip install --no-deps ./dist/*.whl


FROM builder as test

RUN /opt/poetry-venv/bin/poetry install --no-interaction --no-root

RUN /opt/poetry-venv/bin/poetry run poe black --check
RUN /opt/poetry-venv/bin/poetry run poe mypy
RUN /opt/poetry-venv/bin/poetry run poe ruff


FROM base as final

ENV PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app/.venv .venv

VOLUME /data

ENTRYPOINT [ "useless-discord-bot" ]
