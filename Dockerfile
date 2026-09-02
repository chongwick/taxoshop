FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG CPYTHON_REF=f5394c257ce
ARG CPYTHON_HISTORY_DEPTH=5000

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        clang \
        git \
        libbz2-dev \
        libffi-dev \
        libgdbm-compat-dev \
        libgdbm-dev \
        liblzma-dev \
        libncurses5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        llvm \
        tk-dev \
        uuid-dev \
        xz-utils \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

ENV ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:symbolize=1
ENV UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
ENV ASAN_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
ENV LLVM_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
ENV PYTHONMALLOC=malloc

WORKDIR /src

RUN git init cpython \
    && cd cpython \
    && git remote add origin https://github.com/python/cpython.git \
    && git fetch --depth "${CPYTHON_HISTORY_DEPTH}" origin main \
    && git checkout --detach "${CPYTHON_REF}"

WORKDIR /src/cpython

RUN CC=gcc CXX=g++ ./configure \
        --prefix=/opt/python-asan-ubsan \
        --with-address-sanitizer \
        --with-undefined-behavior-sanitizer \
        --without-ensurepip \
        --without-pymalloc \
    && make -j"$(nproc)"

COPY repro/issue_143545.py /src/cpython/repro/issue_143545.py

WORKDIR /src/cpython

CMD ["./python", "./repro/issue_143545.py"]
