FROM ubuntu:24.04 AS build-base

ARG DEBIAN_FRONTEND=noninteractive
ARG CPYTHON_HISTORY_DEPTH=5000

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        clang \
        git \
        libbz2-dev \
        libclang-rt-18-dev \
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

WORKDIR /src

RUN git init cpython \
    && cd cpython \
    && git remote add origin https://github.com/python/cpython.git \
    && git fetch --depth "${CPYTHON_HISTORY_DEPTH}" origin main \

WORKDIR /src/cpython

FROM build-base AS asan-ubsan

ENV ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:symbolize=1
ENV UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
ENV ASAN_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
ENV LLVM_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
ENV PYTHONMALLOC=malloc

RUN CC=gcc CXX=g++ ./configure \
        --prefix=/opt/python-asan-ubsan \
        --with-address-sanitizer \
        --with-undefined-behavior-sanitizer \
        --without-ensurepip \
        --without-pymalloc \
    && make -j"$(nproc)"

COPY repro/issue_143545.py /src/cpython/repro/issue_143545.py

WORKDIR /src/cpython

FROM build-base AS tsan

ENV TSAN_OPTIONS=halt_on_error=1:second_deadlock_stack=1
ENV TSAN_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
ENV LLVM_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
ENV PYTHONMALLOC=malloc

RUN CC=clang CXX=clang++ ./configure \
        --prefix=/opt/python-tsan \
        --with-thread-sanitizer \
        --without-ensurepip \
        --without-pymalloc \
    && make -j"$(nproc)"

WORKDIR /src/cpython

CMD ["./python"]

# Keep the historical ASan/UBSan image as Docker's default build target.
FROM asan-ubsan AS default
