FROM python:3-alpine

RUN apk update && apk add --no-cache libxml2-dev libxslt-dev build-base curl

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install sumy with LSA extra
RUN uv pip install --system "sumy[LSA]" && \
    python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

ENTRYPOINT ["sumy"]
