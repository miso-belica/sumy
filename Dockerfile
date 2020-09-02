FROM python:3.8-alpine

RUN apk update && apk add --no-cache libxml2-dev libxslt-dev build-base

RUN pip install "sumy[LSA]" && \
    python -c "import nltk; nltk.download('punkt')" && \
    rm -rf /root/.cache

ENTRYPOINT ["sumy"]
