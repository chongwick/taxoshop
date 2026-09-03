#!/usr/bin/env bash

set -euo pipefail

image_name="${1:-adjacentbourne-cpython-asan-ubsan}"
output_file="$(mktemp)"

cleanup() {
  rm -f "${output_file}"
}

trap cleanup EXIT

docker build -t "${image_name}" .

set +e
docker run --rm "${image_name}" >"${output_file}" 2>&1
status=$?
set -e

cat "${output_file}"

if [[ "${status}" -eq 0 ]]; then
  echo "expected the sanitizer reproducer to fail, but the container exited successfully" >&2
  exit 1
fi

if ! grep -q "ERROR: AddressSanitizer" "${output_file}"; then
  echo "expected AddressSanitizer output in container logs" >&2
  exit 1
fi

if ! grep -q "heap-use-after-free" "${output_file}"; then
  echo "expected heap-use-after-free in container logs" >&2
  exit 1
fi

if ! grep -q "Modules/_lsprof.c" "${output_file}"; then
  echo "expected lsprof stack frames in container logs" >&2
  exit 1
fi

echo "sanitizer check passed: ASan reported the expected lsprof use-after-free"
