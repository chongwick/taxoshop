# CPython Sanitizer Images

Docker builds of CPython at the revision configured by `CPYTHON_REF` in the
Dockerfile. The default target is AddressSanitizer and UndefinedBehaviorSanitizer
(ASan/UBSan); a separate ThreadSanitizer (TSan) target is also available.

## ASan/UBSan

Build the default image:

```sh
docker build -t adjacentbourne-cpython-asan-ubsan .
```

Run the bundled reproducer for [CPython issue #143545](https://github.com/python/cpython/issues/143545):

```sh
docker run --rm adjacentbourne-cpython-asan-ubsan
```

The reproducer is expected to exit unsuccessfully and print an
`ERROR: AddressSanitizer` heap-use-after-free report.

To build, run, and assert that expected report automatically:

```sh
./verify.sh
```

Pass a different image name if needed:

```sh
./verify.sh my-cpython-asan
```

## TSan

Build the separate TSan image explicitly:

```sh
docker build --target tsan -t taxoshop-cpython-tsan .
```

Start the sanitizer-enabled interpreter:

```sh
docker run --rm --entrypoint /src/cpython/python taxoshop-cpython-tsan -c 'print("TSan CPython started")'
```

TSan reports data races in instrumented native code. The image includes Clang's
matching compiler runtime (`libclang-rt-18-dev`), which is required for TSan on
the ARM64 Docker environment used to validate this image.

## Rebuilds

Docker caches the dependency and CPython-source layers. Rebuilds only recompile
CPython when the selected target or an earlier Dockerfile layer changes. Use
`--no-cache` only when a fully clean rebuild is required.
