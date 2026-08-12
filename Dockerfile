# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder
WORKDIR /app

# lxml (via breadability) has no musllinux wheel for every release, so build it from source here.
RUN apk add --no-cache build-base libxml2-dev libxslt-dev

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    NLTK_DATA=/app/nltk_data

# Every extra except Korean: konlpy's JPype1 extension doesn't load on musl (missing libstdc++
# symbols even with the package installed) and konlpy also requires a JVM at runtime, which we
# don't install here.
#
# Sync only the dependencies first so this layer is cached until pyproject.toml/uv.lock change.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project \
        --extra LSA --extra LexRank --extra Japanese --extra Chinese \
        --extra Hebrew --extra Greek --extra Arabic --extra Thai --extra Polish

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable \
        --extra LSA --extra LexRank --extra Japanese --extra Chinese \
        --extra Hebrew --extra Greek --extra Arabic --extra Thai --extra Polish

RUN uv run --no-sync python -c "import nltk; nltk.download('punkt_tab', download_dir='/app/nltk_data')"

FROM python:3.14-alpine

# Runtime needs only the shared libraries, not the -dev headers/compiler from the builder stage.
RUN apk add --no-cache libxml2 libxslt curl && \
    adduser -D -H sumy

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY --from=builder /app/nltk_data nltk_data

ENV PATH="/app/.venv/bin:$PATH" \
    NLTK_DATA=/app/nltk_data

USER sumy

ENTRYPOINT ["sumy"]
