# Build PHP with AddressSanitizer and UndefinedBehaviorSanitizer enabled.
#
# Example:
#   docker build -f Dockerfile.php -t taxoshop/php-asan-ubsan:current .
#   docker run --rm taxoshop/php-asan-ubsan:current /src/php-src/sapi/cli/php -v
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG PHP_REF=master

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        autoconf \
        bison \
        build-essential \
        ca-certificates \
        clang-12 \
        git \
        libbz2-dev \
        libcurl4-openssl-dev \
        libedit-dev \
        libenchant-2-dev \
        libfreetype6-dev \
        libgmp-dev \
        libicu-dev \
        libjpeg-dev \
        libldap2-dev \
        libonig-dev \
        libpq-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libsnmp-dev \
        libsodium-dev \
        libwebp-dev \
        libxml2-dev \
        libxslt1-dev \
        libzip-dev \
        llvm-12 \
        pkg-config \
        re2c \
        zlib1g-dev \
    && ln -s /usr/bin/llvm-symbolizer-12 /usr/local/bin/llvm-symbolizer \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

RUN git clone --depth 1 --branch "${PHP_REF}" https://github.com/php/php-src.git

WORKDIR /src/php-src

# This is the broad debug configuration used for PHP sanitizer/fuzzing work.
# PHP's sanitizer configure options add the corresponding compiler and linker
# flags; ZEND_VERIFY_TYPE_INFERENCE enables additional VM type-inference checks.
RUN ./buildconf --force \
    && CC=clang-12 \
       CXX=clang++-12 \
       CFLAGS='-DZEND_VERIFY_TYPE_INFERENCE' \
       CXXFLAGS='-DZEND_VERIFY_TYPE_INFERENCE' \
       ./configure \
           --enable-debug \
           --enable-address-sanitizer \
           --enable-undefined-sanitizer \
           --enable-re2c-cgoto \
           --enable-fpm \
           --enable-litespeed \
           --enable-phpdbg-debug \
           --enable-zts \
           --enable-bcmath \
           --enable-calendar \
           --enable-dba \
           --enable-dl-test \
           --enable-exif \
           --enable-ftp \
           --enable-gd \
           --enable-gd-jis-conv \
           --enable-mbstring \
           --enable-pcntl \
           --enable-shmop \
           --enable-soap \
           --enable-sockets \
           --enable-sysvmsg \
           --enable-zend-test \
           --with-zlib \
           --with-bz2 \
           --with-curl \
           --with-enchant \
           --with-gettext \
           --with-gmp \
           --with-mhash \
           --with-ldap \
           --with-libedit \
           --with-readline \
           --with-snmp \
           --with-sodium \
           --with-xsl \
           --with-zip \
           --with-mysqli \
           --with-pdo-mysql \
           --with-pdo-pgsql \
           --with-pgsql \
           --with-sqlite3 \
           --with-pdo-sqlite \
           --with-webp \
           --with-jpeg \
           --with-freetype \
           --enable-sigchild \
           --with-pcre-jit \
           --with-iconv \
    && make -j"$(nproc)"

# Zend's custom allocator hides allocations from ASan. Disable it for sanitizer
# runs so heap UAF and OOB reports point to the original allocation site.
ENV USE_ZEND_ALLOC=0
ENV ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:symbolize=1
ENV UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
ENV ASAN_SYMBOLIZER_PATH=/usr/local/bin/llvm-symbolizer
ENV LLVM_SYMBOLIZER_PATH=/usr/local/bin/llvm-symbolizer

CMD ["/src/php-src/sapi/cli/php"]
