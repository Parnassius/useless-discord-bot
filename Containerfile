FROM python:3.14-alpine as base

ENV PYTHONUNBUFFERED=1

ENV BOT_CONFIG_PATH=/data
WORKDIR /app

RUN apk add --no-cache cairo


FROM base as builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_FROZEN=1
ENV UV_LINK_MODE=copy
ENV UV_NO_EDITABLE=1
ENV UV_NO_SYNC=1

COPY --from=ghcr.io/astral-sh/uv /uv /bin/uv

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev


FROM builder as test

RUN apk add --no-cache make

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

RUN make lint


FROM base as final

ENV PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app/.venv .venv

VOLUME /data

ENTRYPOINT [ "useless-discord-bot" ]
