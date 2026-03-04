FROM postgres:15-alpine

RUN apk add --no-cache --virtual .build-deps \
    git \
    build-base \
    clang \
    llvm \
    postgresql-dev \
    && cd /tmp \
    && git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd / \
    && rm -rf /tmp/pgvector \
    && apk del .build-deps
