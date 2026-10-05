#!/bin/bash
docker run --rm -v "$PWD":/audit taxoshop/cruby-asan-ubsan:current bash -c \
"cd /src/ruby && UBSAN_OPTIONS=halt_on_error=0:print_stacktrace=0:suppressions=/audit/ubsan.supp ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:symbolize=1:halt_on_error=1 ./ruby --disable-gems -I. -I.ext/aarch64-linux -I.ext/common -Ilib /audit/$1 2>&1"
