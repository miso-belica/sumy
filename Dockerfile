FROM python:alpine

RUN apk update && apk add --no-cache libxml2-dev libxslt-dev build-base
RUN pip install sumy
RUN python -c "import nltk; nltk.download('punkt')"
RUN pip install numpy
RUN rm -fr /root/.cache
ENTRYPOINT ["sumy"] 
