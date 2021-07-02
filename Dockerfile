FROM python:3.9.5-slim-buster as builder
WORKDIR /wheels

# handle openfaas flask essentials modules
COPY requirements.txt   .

RUN pip install -U pip \
    && pip wheel -r ./requirements.txt


FROM python:3.9.5-slim-buster

ENV PORT=8080

# Alternatively use ADD https:// (which will not be cached by Docker builder)
RUN apt-get update -y \
    && apt-get install -y curl jq vim \
    && ln -sf /bin/bash /bin/sh \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY --from=builder /wheels /wheels
RUN pip install -U pip \
    && pip install --no-index -r /wheels/requirements.txt -f /wheels \
    && rm -rf /wheels /root/.cache/pip/*

RUN find /usr/local -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
            -o \( -type f -a -name 'wininst-*.exe' \) \
        \) -exec rm -rf '{}' +;

WORKDIR /app
ADD . /app

# Run a WSGI server to serve the application. gunicorn must be declared as
# a dependency in requirements.txt.
CMD gunicorn -b :$PORT -k eventlet -w 1 sioproject.main:app
