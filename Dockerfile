# syntax = docker/dockerfile:1.0-experimental

FROM python:2.7.18

RUN pip install git+https://github.com/PaulUithol/python-pbkdf2
RUN pip install pycrypto

ENV APP_ROOT /work
RUN mkdir -p "$APP_ROOT"
WORKDIR $APP_ROOT

RUN apt-get update && \
    # for shell completion
    apt-get install -y --no-install-recommends zsh && \
    # Cleaning
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    find /usr/share/doc -depth -type f ! -name copyright | xargs rm || true && \
    find /usr/share/doc -empty | xargs rmdir || true && \
    rm -rf /usr/share/man/* /usr/share/groff/* /usr/share/info/* && \
    rm -rf /usr/share/lintian/* /usr/share/linda/* /var/cache/man/* && \
    rm -rf /var/lib/mysql/*
