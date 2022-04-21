FROM python:3-alpine

RUN apk update && apk add --no-cache libxml2-dev libxslt-dev build-base

RUN pip install "sumy[LSA]" && \
    python -c "import nltk; nltk.download('punkt')" && \
    pip cache purge

ENTRYPOINT ["sumy"]
