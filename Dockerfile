# Build SQLite with AddressSanitizer + UndefinedBehaviorSanitizer.
#
# Usage:
#   docker build -t sqlite-asan .
#   docker run --rm -it sqlite-asan            # drops you in the shell built with ASan/UBSan
#   docker run --rm sqlite-asan sqlite3 :memory: "select sqlite_version();"
#
FROM ubuntu:24.04

# tcl is needed by SQLite's build/test tooling; the rest is a normal C toolchain.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        clang \
        llvm \
        libclang-rt-18-dev \
        tcl-dev \
        tclsh \
        zlib1g-dev \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY sqlite/ /src/

# Configure with a clean toolchain (sanitizer flags here break configure's tiny
# probe programs), then inject the sanitizers at build time via $(CFLAGS.core).
# That variable is appended only to the SQLite compile *and* link steps, and is
# NOT passed to the build-time code generators (lemon, mkkeywordhash, jimsh) --
# unlike $(OPTS), which is also forwarded to lemon as CLI args and breaks it.
#
# Sanitizer flags:
#  - address: heap/stack/global overflow + use-after-free
#  - undefined: signed overflow, misaligned access, bad shifts, etc.
#  - fno-sanitize-recover=all: turn every finding into a hard abort (good for CI)
ENV CC=clang
ENV SAN="-g -O1 -fno-omit-frame-pointer -fsanitize=address,undefined -fno-sanitize-recover=all"

RUN ./configure --enable-all && \
    make sqlite3 CFLAGS.core="$SAN" && \
    cp sqlite3 /usr/local/bin/sqlite3

# Halt on the first UBSan diagnostic and print readable ASan reports.
ENV ASAN_OPTIONS=abort_on_error=1:halt_on_error=1:detect_leaks=1
ENV UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1

CMD ["sqlite3"]
