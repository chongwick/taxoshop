#!/bin/bash
# Run inside the asan-ubsan container. Runs the CPython regression suite under
# ASan+UBSan and captures every sanitizer diagnostic without aborting on the
# first one, so we can triage the full population of findings.
#
# Usage (inside container, from /src/cpython):
#   bash /work/run_suite_ubsan.sh 2>&1 | tee /work/suite.log
set -u

# Collect ALL findings: do not halt, do not abort. Log UBSan to files.
export UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=0:log_path=/work/ubsan"
export ASAN_OPTIONS="detect_leaks=0:abort_on_error=0:halt_on_error=0:symbolize=1:log_path=/work/asan"
export ASAN_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
export LLVM_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
export PYTHONMALLOC=malloc

cd /src/cpython
# -j: parallel; -uall: enable all resource-heavy resources; keep it broad.
# Exclude tests that are known-flaky under ASan for time, but keep memory-safety relevant ones.
./python -m test -j"$(nproc)" -uall --timeout=600 \
    -x test_faulthandler \
    2>&1
echo "=== SUITE EXIT $? ==="
echo "=== UBSAN LOGS ==="
ls -la /work/ubsan.* 2>/dev/null || echo "(no ubsan logs)"
echo "=== ASAN LOGS ==="
ls -la /work/asan.* 2>/dev/null || echo "(no asan logs)"
