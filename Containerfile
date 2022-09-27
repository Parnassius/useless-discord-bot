FROM python:3.10-slim as base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libcairo2


FROM base as builder

RUN python -m venv /opt/poetry-venv
RUN /opt/poetry-venv/bin/pip install --upgrade pip setuptools
RUN /opt/poetry-venv/bin/pip install poetry

RUN python -m venv .venv

COPY poetry.lock pyproject.toml .
RUN /opt/poetry-venv/bin/poetry install --no-interaction --only main --no-root

COPY . .
RUN /opt/poetry-venv/bin/poetry build --no-interaction --format wheel


FROM base as final

COPY --from=builder /app/.venv .venv
COPY --from=builder /app/dist .

RUN .venv/bin/pip install *.whl
RUN rm *.whl

VOLUME /data

ENTRYPOINT [ ".venv/bin/bot" ]
