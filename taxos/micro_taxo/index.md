# CPython bug instance reports

363 reports. Each file contains the full issue body and all comments verbatim.

| Issue | Title | Sanitizer records | Fix data |
|---|---|---|---|
| [#100086](gh_100086.md) | Add more details about the Python build in sys.version | 0 | Yes |
| [#100773](gh_100773.md) | `Py_Initialize()` still leaks in libpython3.11 | 1 | Yes |
| [#100795](gh_100795.md) | segfault in a docker container on host with ipv6 disabled when using  getaddrinfo from socket.py | 0 | Yes |
| [#101180](gh_101180.md) | Modules/cjkcodecs/_codecs_iso2022.c - read out of bounds | 4 | Yes |
| [#101975](gh_101975.md) | Potential SegFault with multithreading garbage collection. | 1 | Yes |
| [#102509](gh_102509.md) | cpython3:fuzz_builtin_unicode: Use-of-uninitialized-value in maybe_small_long | 0 | Yes |
| [#103718](gh_103718.md) | Not closing an f-string leads to a use-after-free | 2 | Yes |
| [#104472](gh_104472.md) | ASAN failure was detected while running test_threading | 1 | Yes |
| [#104791](gh_104791.md) | LeakSanitizer at build time using --with-address-sanitizer on Ubuntu 22.04 #AddressSanitizer #ASAN | 2 | — |
| [#106012](gh_106012.md) | Crash in test_import: Assertion error about monitoring version. | 1 | Yes |
| [#106914](gh_106914.md) | Use of uninitialized memory in Objects/longobject.c | 1 | — |
| [#108253](gh_108253.md) | heap-use-after-free in _PyFunction_LookupByVersion | 1 | Yes |
| [#109128](gh_109128.md) | Address sanitizer tests fail: env changed | 0 | Yes |
| [#109580](gh_109580.md) | test_perf_profiler: test_trampoline_works_with_forks() failed on Address Sanitizer CI | 0 | Yes |
| [#110097](gh_110097.md) | test_concurrent_futures.test_process_pool: test_map_timeout failed | 0 | Yes |
| [#111178](gh_111178.md) | UBSan: Calling a function through pointer to incorrect function type is undefined behavior | 2 | Yes |
| [#111339](gh_111339.md) | Crashes and errors in test_embed with PYTHONUOPS=1 | 0 | Yes |
| [#111942](gh_111942.md) | TextIOWrapper.reconfigure() crashes if encoding is not string or None | 0 | Yes |
| [#113055](gh_113055.md) | Memory leak on executables embedded with 3.13 | 1 | Yes |
| [#113190](gh_113190.md) | python3.12 introduces numerous memory leaks (as reported by ASAN) | 4 | Yes |
| [#113576](gh_113576.md) | Possible `heap-use-after-free` in ctypes in Python 3.12 | 2 | Yes |
| [#113591](gh_113591.md) | Segfaults on 3.12 when using PySR and running Julia's GC | 1 | Yes |
| [#113602](gh_113602.md) | Objects/call.c:342: PyObject *_PyObject_Call(PyThreadState *, PyObject *, PyObject *, PyObject *): Assertion `!_PyErr_Occurred(tstate)' failed. | 1 | Yes |
| [#113720](gh_113720.md) | [not crashing] runtime error in tokenizer (pointer index expression overflow) | 2 | — |
| [#113956](gh_113956.md) | `_Py_SetImmortal` must be run on allocating thread (no-gil) | 1 | Yes |
| [#114050](gh_114050.md) | crash in long_vectorcall in longobject.c | 1 | Yes |
| [#114083](gh_114083.md) | Python/flowgraph.c:497: _Bool no_redundant_jumps(cfg_builder *): Assertion `0' failed. | 1 | Yes |
| [#114106](gh_114106.md) | segfault when compiling gc referrers referents with frozenset | 1 | — |
| [#114331](gh_114331.md) | mimalloc should fail to allocate 784 271 641 GiB: test_decimal killed by the Linux kernel with OOM on a Free Threading build | 0 | Yes |
| [#114453](gh_114453.md) | pycore_interp.h: field has incomplete type 'struct _dtoa_state' | 0 | — |
| [#115243](gh_115243.md) | Use After Free in deque_index_impl | 1 | Yes |
| [#115378](gh_115378.md) | Segmentation Fault in pthread_getcpuclockid function in time module | 1 | — |
| [#116259](gh_116259.md) | [3.11] ./config.status: line 527: 0a1,698: command not found | 0 | — |
| [#116510](gh_116510.md) | CPython 3.12 embedded in WeeChat causes segfault on subsequent calls to Py_EndInterpreter | 1 | Yes |
| [#116550](gh_116550.md) | Reading undefined value in pickle module w/memory sanitizer enabled | 2 | — |
| [#116886](gh_116886.md) | CIFuzz build failures - _freeze_module segfaults during the build, fuzz testing doesn't start. | 1 | Yes |
| [#116891](gh_116891.md) | Error configuring with TSAN | 0 | — |
| [#116912](gh_116912.md) | TSan: data race accessing socket fd | 2 | — |
| [#118074](gh_118074.md) | global-buffer-overflow in test_opt.py | 1 | Yes |
| [#118113](gh_118113.md) | Optimizer/executor crash when using address sanitizer | 1 | — |
| [#118729](gh_118729.md) | "thread sanitizer" (tsan) CI job is hanging | 0 | Yes |
| [#119447](gh_119447.md) | 1506-007 (S) "struct _dtoa_state" is undefined on AIX | 0 | Yes |
| [#119462](gh_119462.md) | Python 3.13b repeatedly setting superclass attribute in subclass leads to crashes | 2 | Yes |
| [#120289](gh_120289.md) | Use After Free in initContext(_lsprof.c) | 1 | Yes |
| [#120298](gh_120298.md) | Use After Free in list_richcompare_impl  | 1 | Yes |
| [#120378](gh_120378.md) | Segmentation Fault in _curses | 1 | Yes |
| [#120696](gh_120696.md) | faulthandler will hang the process with a TSAN and free-thread build Python | 0 | Yes |
| [#121065](gh_121065.md) | Thread sanitizer (free-threading) tests fail: test_signal raises RecursionError | 0 | Yes |
| [#121112](gh_121112.md) | [marshal] diffoscope crash when loading PYC files: memory corruption | 0 | — |
| [#121275](gh_121275.md) | Some tests in test_smtplib and test_logging failed when Python is configured with `--disable-ipv6` | 0 | Yes |
| [#121390](gh_121390.md) | Memory leak in tracemalloc | 1 | Yes |
| [#121637](gh_121637.md) | Python/compile.c:7482: int compute_code_flags(struct compiler *): Assertion `IS_TOP_LEVEL_AWAIT(c) \|\| _PyST_IsFunctionLike(ste)' failed | 1 | Yes |
| [#121847](gh_121847.md) | Build failure with "--with-address-sanitizer" flag | 1 | Yes |
| [#122026](gh_122026.md) | Parser/lexer/lexer.c:1218: int tok_get_normal_mode(struct tok_state *, tokenizer_mode *, struct token *): Assertion `current_tok->curly_bracket_depth >= 0' failed. | 1 | Yes |
| [#122136](gh_122136.md) | test.test_asyncio.test_server.TestServer2.test_abort_clients consistently fails on Linux 6.10.x | 0 | Yes |
| [#122431](gh_122431.md) | Segmentation Fault in append_history_file of readline  | 1 | Yes |
| [#124001](gh_124001.md) | PyFaulthandler: heap-buffer-overflow | 5 | — |
| [#124378](gh_124378.md) | New test_ttk failure on Mac: "bad screen distance" | 0 | Yes |
| [#124878](gh_124878.md) | race condition in threading when interpreter finalized while daemon thread runs (thread sanitizer identified) | 1 | Yes |
| [#125318](gh_125318.md) | Segfault from `zoneinfo` with custom DateTime class | 0 | Yes |
| [#125515](gh_125515.md) | Multiple unused code warnings in `Python/generated_cases.c.h` | 0 | Yes |
| [#126445](gh_126445.md) | Thread sanitizer (free-threading) / Thread sanitizer test failure | 0 | — |
| [#127563](gh_127563.md) | UBSan: misaligned memory loads in `Objects/dictobject.c` | 1 | Yes |
| [#127971](gh_127971.md) | ASan: heap-buffer-overflow in ucs2lib_default_find | 1 | Yes |
| [#128013](gh_128013.md) | Data race in PyUnicode_AsUTF8AndSize under free-threading | 1 | Yes |
| [#128050](gh_128050.md) | Race between `partial_vectorcall_fallback` and `_PyVectorcall_FunctionInline` under free-threading | 2 | Yes |
| [#128100](gh_128100.md) | Race between _PyObject_GenericGetAttrWithDict and ensure_nonmanaged_dict under free-threading | 1 | Yes |
| [#128130](gh_128130.md) | Race on `_PyRuntime.signals.unhandled_keyboard_interrupt` when calling `eval()` concurrently in free-threading mode | 3 | Yes |
| [#128133](gh_128133.md) | Race in bytes_hash under free-threading | 1 | Yes |
| [#128137](gh_128137.md) | Race in PyUnicode_InternFromString under free-threading | 1 | Yes |
| [#128144](gh_128144.md) | Race between PyMember_GetOne and PyMember_SetOne for _Py_T_OBJECT members under freethreading | 1 | Yes |
| [#128212](gh_128212.md) | Race between ` PyUnicode_SET_UTF8` and `_PyUnicode_CheckConsistency` | 1 | Yes |
| [#129019](gh_129019.md) | Compiling 3.13.1 fails when /usr/local/include/pyconfig.h is outdated | 0 | Yes |
| [#129701](gh_129701.md) | Data race in `intern_common` when interning str objects in the free threading build | 1 | Yes |
| [#129824](gh_129824.md) | Various data races in subinterpreter tests under TSAN | 0 | Yes |
| [#129838](gh_129838.md) | _Py_NO_SANITIZE_UNDEFINED is defined twice when compiling with recent GCC | 0 | Yes |
| [#130019](gh_130019.md) | Data race in `_PyType_AllocNoTrack` in free threaded build | 1 | Yes |
| [#130091](gh_130091.md) | Data race in `PyThread_tss_delete` and `_PyThreadState_Attach` | 1 | Yes |
| [#130421](gh_130421.md) | TSAN failures seen running PyO3 tests with the free-threaded build | 3 | Yes |
| [#130555](gh_130555.md) | Use after free in `PyDict_Clear()` due to re-entrancy | 1 | Yes |
| [#130605](gh_130605.md) | `test_concurrent_futures` TSAN failures | 1 | Yes |
| [#130977](gh_130977.md) | Data races in free-threaded python on Py_buffer use | 1 | Yes |
| [#131325](gh_131325.md) | data race while running `test_asyncio.test_sendfile` in TSAN | 1 | Yes |
| [#132097](gh_132097.md) | UBSan: runtime undefined behaviours when using `-fsanitize=undefined -fno-sanitize-recover` | 1 | Yes |
| [#132869](gh_132869.md) | Crash due to racy read in dictobject do_lookup under free threading | 0 | Yes |
| [#132886](gh_132886.md) | Socket file descriptor races in GIL-enabled build | 1 | Yes |
| [#133157](gh_133157.md) | UBsan: Remove _Py_NO_SANITIZE_UNDEFINED | 0 | Yes |
| [#133473](gh_133473.md) | TSan data races from test_queue with free threading | 1 | — |
| [#134457](gh_134457.md) | Type of vectorcall nargs inconsistent | 1 | — |
| [#135618](gh_135618.md) | ASan detects memory leaks in Python REPL during immediate exit after startup | 3 | — |
| [#135636](gh_135636.md) | Use After Free on Py_INCREF | 1 | — |
| [#135637](gh_135637.md) | SEGV on _Py_type_getattro_impl | 1 | — |
| [#135774](gh_135774.md) | clang -fsanitize=memory detected error with the trivial program that embeds the Python interpreter | 2 | — |
| [#135830](gh_135830.md) | [MSVC][ASAN] Cpython failed to run test_call test_functools tests with ASAN using MSVC on windows | 1 | — |
| [#136872](gh_136872.md) | The configure script doesn't allow running ASan with PyMalloc | 2 | — |
| [#138756](gh_138756.md) | PyInitConfig_Free() doesn't release memory allocated by PyInitConfig_SetStr() | 1 | Yes |
| [#139116](gh_139116.md) | Potential deadlock in test_tracemalloc with the FT build and tail-call dispatch. | 0 | Yes |
| [#139210](gh_139210.md) | heap-use-after-free `_elementtree_XMLParser__setevents_impl` | 1 | Yes |
| [#139269](gh_139269.md) | JIT: UB: unaligned store in `patch_*` functions | 1 | Yes |
| [#139400](gh_139400.md) | Heap-use-after-free issue in `pyexpat` related to `.ExternalEntityParserCreate` | 1 | Yes |
| [#139540](gh_139540.md) | JIT executors are not properly freed | 2 | Yes |
| [#139748](gh_139748.md) | Argument Clinic does not handle error paths for converters creating a strong reference to a PyObject | 1 | Yes |
| [#139749](gh_139749.md) | memory leak after ValueError in JIT | 1 | — |
| [#139750](gh_139750.md) | memory leak with glob and mock in JIT | 1 | — |
| [#139751](gh_139751.md) | symtable ValueError and memory leak | 2 | — |
| [#139827](gh_139827.md) | memory leak in email message make mixed with long boundary | 1 | — |
| [#139834](gh_139834.md) | JIT: Segfault in _Py_LazyJitTrampoline with ASan/UBSan enabled | 3 | Yes |
| [#139951](gh_139951.md) | Potentially serious regression in garbage collector performance in Python 3.14 | 1 | Yes |
| [#139988](gh_139988.md) | Leak with a Union object when an argument is not a type | 1 | Yes |
| [#140067](gh_140067.md) | Memory leak in test_sys with subinterpreters creation (AddressSanitizer detection) | 1 | Yes |
| [#140120](gh_140120.md) | Memory leak in `hmac` module with HACL* backend detected by AddressSanitizer | 1 | Yes |
| [#140138](gh_140138.md) | TSAN failure with free-threaded build, test_daemon_threads_fatal_error | 1 | Yes |
| [#140159](gh_140159.md) | Build Failure in posixmodule.c with Clang, ThreadSanitizer, and free-threaded build enabled | 1 | Yes |
| [#140257](gh_140257.md) | ThreadSanitizer: data race in interpreter_clear() vs take_gil() during finalization with daemon threads | 1 | Yes |
| [#140260](gh_140260.md) | ThreadSanitizer: data race in _struct module initialization with InterpreterPoolExecutor (free-threading build) | 1 | Yes |
| [#140263](gh_140263.md) | TSan data race in test_capi.test_lock_two_threads | 1 | Yes |
| [#140267](gh_140267.md) | ThreadSanitizer reports thread leak in multiprocessing.Manager accepter thread | 1 | Yes |
| [#140272](gh_140272.md) | Memory leak in _gdbm.gdbm.clear() method: missing free() for gdbm_firstkey() result | 1 | Yes |
| [#140301](gh_140301.md) | Memory leak in test_capi with subinterpreter creation | 1 | Yes |
| [#140306](gh_140306.md) | Memory leak in test__interpchannels: _PyXIData_New not freed in channel_send | 1 | Yes |
| [#140332](gh_140332.md) | MemorySanitizer: use-of-uninitialized-value in _ssl.txt2obj via OpenSSL's OBJ_txt2obj | 1 | — |
| [#140354](gh_140354.md) | fail build when enable-experimental-jit on Android | 0 | — |
| [#140398](gh_140398.md) | Memory leaks in readline module when PySys_Audit fails | 1 | Yes |
| [#140404](gh_140404.md) | LeakSanitizer detects memory leaks in test_import with _testsinglephase module in subinterpreter | 1 | — |
| [#140406](gh_140406.md) | Memory leak when `object.__hash__` returns a non-`int` value | 1 | Yes |
| [#140408](gh_140408.md) | python crash at ffi call | 1 | — |
| [#140409](gh_140409.md) | heap-buffer-overflow in ctypes.create_string_buffer _ctypes_test.my_qsort | 2 | — |
| [#140410](gh_140410.md) | SystemError: invalid maximum character passed to PyUnicode_New | 0 | — |
| [#140431](gh_140431.md) | Segfault in gc_free_threading.c after PR #140262 with ASAN build and free-threading tests | 2 | Yes |
| [#140442](gh_140442.md) | LeakSan: 80-byte leak at shutdown after atexit.register of bound list.append(-0.0) | 1 | Yes |
| [#140462](gh_140462.md) | SEGV due to `ncurses` allowing sizes to be excessively large | 2 | — |
| [#140471](gh_140471.md) | global-buffer-overflow PyUnicode_GET_LENGTH cpython/unicodeobject.h | 1 | Yes |
| [#140474](gh_140474.md) | memory leak in array.array | 1 | Yes |
| [#140492](gh_140492.md) | heap buffer overflow in ast _copy_characters | 1 | — |
| [#140493](gh_140493.md) | memory leak in multi threading with fork | 1 | — |
| [#140496](gh_140496.md) | cpython crash (heap-use-after-free) _Py_IsImmortal Include/internal/pycore_stackref.h | 1 | — |
| [#140497](gh_140497.md) | cpython crash (heap-buffer-overflow) Python/generated_cases.c.h _PyEval_EvalFrameDefault | 1 | — |
| [#140517](gh_140517.md) | Memory leak in `map_next` in strict mode in case of error | 1 | Yes |
| [#140530](gh_140530.md) | Reference leak when failing to raise from an exception cause | 1 | Yes |
| [#140551](gh_140551.md) | Crash in `dict` if `hash` `__eq__` function has side effects | 1 | Yes |
| [#140564](gh_140564.md) | SystemError: Objects/codeobject.c bad argument to internal function | 0 | — |
| [#140576](gh_140576.md) | SystemError in _generate_tokens_from_c_tokenizer | 0 | Yes |
| [#140590](gh_140590.md) | SEGV functools _Py_dict_lookup | 1 | Yes |
| [#140593](gh_140593.md) | Memory leak in function `my_ElementDeclHandler` of `pyexpat` | 2 | Yes |
| [#140594](gh_140594.md) | heap-buffer-overflow PyOS_StdioReadline Parser/myreadline.c | 1 | Yes |
| [#140607](gh_140607.md) | heap-buffer-overflow in _io__RawIOBase_read | 1 | Yes |
| [#140608](gh_140608.md) | ASAN: double-free in SSL handshake | 1 | — |
| [#140631](gh_140631.md) | Indirect memory leak when instantiating hashlib types | 1 | — |
| [#140634](gh_140634.md) | heap-buffer-overflow deepcopy posix_param | 1 | Yes |
| [#140650](gh_140650.md) | SystemError in io.BufferedWriter.close when closed errors | 0 | Yes |
| [#140651](gh_140651.md) | heap-use-after-free in pickle posix | 1 | — |
| [#140652](gh_140652.md) | SEGV in module interpchannels | 1 | Yes |
| [#140750](gh_140750.md) | JSON: heap-buffer-overflow in encoder caused by indentation caching | 1 | Yes |
| [#140751](gh_140751.md) | SystemError PyState_AddModule called on module with slots in testmultiphase | 0 | — |
| [#140776](gh_140776.md) | SEGV when changing `co_consts` of a function definition | 1 | — |
| [#140777](gh_140777.md) | AddressSanitizer: BUS abort in multiprocessing.shared_memory | 1 | — |
| [#140798](gh_140798.md) | Memory leak with `threading.local` when tracing is active | 1 | Yes |
| [#140802](gh_140802.md) | heap-buffer-overflow in pycore_interpframe.h _PyFrame_Initialize | 1 | — |
| [#140815](gh_140815.md) | SEGV in `faulthandler.dump_traceback_later` | 1 | Yes |
| [#140860](gh_140860.md) | indirect memory leak with audit hook | 2 | Yes |
| [#140935](gh_140935.md) | Assertion failure in Objects/codeobject.c advance_with_locations | 0 | — |
| [#140936](gh_140936.md) | Assertion failure in Python/optimizer.c _PyOptimizer_Optimize in JIT | 0 | Yes |
| [#140939](gh_140939.md) | memory leak in `_PyBytes_FormatEx` error path | 1 | Yes |
| [#141044](gh_141044.md) | memory leak in threading stack size | 2 | — |
| [#141307](gh_141307.md) | Assertion failure in Objects/call.c `_PyObject_VectorcallDictTstate: Assertion `!_PyErr_Occurred(tstate)' failed.` | 0 | — |
| [#141311](gh_141311.md) | Assertion failure in Modules/_io/bytesio.c `_io_BytesIO_readinto_impl: Assertion 'self->pos + len < PY_SSIZE_T_MAX' failed.` | 0 | Yes |
| [#141312](gh_141312.md) | Assertion failure in Objects/rangeobject.c `compute_range_length: Assertion PyLong_Check(start)' failed` | 0 | Yes |
| [#141314](gh_141314.md) | Assertion failure in Modules/_io/textio.c `_io_TextIOWrapper_tell_impl: Assertion 'skip_back <= PyBytes_GET_SIZE(next_input)' failed` | 0 | Yes |
| [#141336](gh_141336.md) | Assertion failure in Objects/unicodeobject.c `_PyUnicode_DecodeUnicodeEscapeInternal2: Assertion 'end - s <= writer.size - writer.pos' failed` | 0 | Yes |
| [#141338](gh_141338.md) | SystemError buffer overflow in `fcntl.fcntl` | 0 | — |
| [#141372](gh_141372.md) | memory leak in `cProfile.Profile` | 1 | — |
| [#141390](gh_141390.md) | Assertion failure in Python/generated_cases.c.h `PyObject *_PyEval_EvalFrameDefault(PyThreadState *, _PyInterpreterFrame *, int): Assertion 'oparg == co->co_nfreevars' failed` | 0 | — |
| [#141542](gh_141542.md) | memory leak in `_PyJit_TryInitializeTracing` | 1 | — |
| [#141621](gh_141621.md) | UBSan SEGV in `_Py_LazyJitTrampoline` when building with Clang and `--with-undefined-behavior-sanitizer` + experimental JIT | 2 | — |
| [#141648](gh_141648.md) | JIT segfault or aborts from shape confusion code | 0 | Yes |
| [#142276](gh_142276.md) | JIT Assertion failure `_POP_TOP_INT.c:119: _Py_CODEUNIT *_JIT_ENTRY(_PyInterpreterFrame *, _PyStackRef *, PyThreadState *): Assertion 'PyLong_CheckExact(PyStackRef_AsPyObjectBorrow(value))' failed` | 0 | Yes |
| [#142448](gh_142448.md) | Assertion failure at Python/generated_cases.c.h:10059 `PyObject *_PyEval_EvalFrameDefault(PyThreadState *, _PyInterpreterFrame *, int): Assertion 'STACK_LEVEL() == 0' failed` | 0 | Yes |
| [#142451](gh_142451.md) | HMAC.copy() does not correctly copy its attributes | 0 | Yes |
| [#142476](gh_142476.md) | ASan memory leak in test_gc with --enable-experimental-jit (allocate_executor) | 1 | Yes |
| [#142554](gh_142554.md) | Out-of-bound Read in `pylong_int_divmod` via override `_pylong.int_divmod` method | 1 | Yes |
| [#142555](gh_142555.md) | `array`: `*_setitem` functions & co may crash on re-entrant `__index__` | 1 | Yes |
| [#142556](gh_142556.md) | Use-after-free in `asyncio` Task deallocation via re-registering task in `call_exception_handler` | 1 | Yes |
| [#142557](gh_142557.md) | Use-after-free in `bytearray_mod` (bytes formatting) via re-entrant `__repr__` method | 1 | Yes |
| [#142558](gh_142558.md) | Use-after-free in `bytearray.count` via re-entrant `__index__` | 1 | Yes |
| [#142559](gh_142559.md) | Use-after-free in `bytearray.find` via re-entrant `__index__` | 1 | — |
| [#142560](gh_142560.md) | Use-after-free in `bytearray` search methods via re-entrant `__index__` | 1 | Yes |
| [#142594](gh_142594.md) | Null pointer dereference in `TextIOWrapper.close()` via re-entrant `closed` property that detaches `buffer` | 1 | Yes |
| [#142595](gh_142595.md) | Heap-buffer-overflow in `_decimal_exec` via overriding `collections.namedtuple` | 1 | Yes |
| [#142629](gh_142629.md) | JIT: Global buffer overflow in `_PyUOpPrint` when running with `PYTHON_LLTRACE=4` | 1 | Yes |
| [#142637](gh_142637.md) | Use-after-free in several `OrderedDict` operations via re-entrant `__eq__` | 1 | — |
| [#142661](gh_142661.md) | Assertion failure at Python/instruction_sequence.c:121: `int _PyInstructionSequence_Addop(instr_sequence *, int, int, location): Assertion 'OPCODE_HAS_ARG(opcode) \|\| HAS_TARGET(opcode) \|\| oparg == 0' failed` | 0 | — |
| [#142663](gh_142663.md) | Use-after-free in `memoryview` comparison via re-entrant `struct.Struct.unpack_from` | 1 | Yes |
| [#142664](gh_142664.md) | Use-after-free in `memoryview.__hash__` via re-entrant `__hash__` | 1 | Yes |
| [#142665](gh_142665.md) | Use-after-free in `memoryview` slicing via re-entrant `__index__` | 1 | Yes |
| [#142717](gh_142717.md) | SEGV race condition with heapq in JIT | 1 | — |
| [#142718](gh_142718.md) | SEGV at Python/generated_cases.c.h _PyEval_EvalFrameDefault in JIT | 1 | Yes |
| [#142731](gh_142731.md) | Use-after-free in `builtin_delattr_impl` and `builtin_setattr_impl` via re-entrant `__hash__` | 1 | Yes |
| [#142732](gh_142732.md) | Use-after-free in `itertools.zip_longest_next/islice/batched` via re-entrant iterator | 1 | Yes |
| [#142734](gh_142734.md) | Use-after-free in `OrderedDict.copy` via re-entrant `__getitem__` | 1 | Yes |
| [#142736](gh_142736.md) | Assertion failure dis null byte | 0 | — |
| [#142737](gh_142737.md) | assertion failure at Objects/call.c:618: `PyObject *callmethod(PyThreadState *, PyObject *, const char *, struct __va_list_tag *): Assertion 'callable != NULL' failed.` | 0 | Yes |
| [#142781](gh_142781.md) | Type confusion in `zoneinfo_ZoneInfo_impl` via overridden cache `setdefault()` | 1 | Yes |
| [#142782](gh_142782.md) | Use-after-free in `zone_from_strong_cache` via re-entrant `ZoneInfo.clear_cache()` from key `__eq__` | 1 | — |
| [#142783](gh_142783.md) | Use-after-free in `zoneinfo.get_weak_cache` via weak DECREF assumption | 1 | Yes |
| [#142787](gh_142787.md) | assertion failure at Modules/_sqlite/blob.c:146: `PyObject *read_multiple(pysqlite_Blob *, Py_ssize_t, Py_ssize_t): Assertion 'offset < sqlite3_blob_bytes(self->blob)' failed` | 0 | Yes |
| [#142828](gh_142828.md) | Use-after-free in `atexit.unregister` via re-entrant `__eq__` | 1 | — |
| [#142829](gh_142829.md) | Use-after-free in `Context.__eq__` via re-entrant `ContextVar.set` | 1 | Yes |
| [#142830](gh_142830.md) | Use-after-free in `sqlite3` progress handler via re-entrant `__bool__` | 1 | Yes |
| [#142831](gh_142831.md) | Use-after-free in `json.encoder` mapping iteration via re-entrant key encoder | 1 | Yes |
| [#142882](gh_142882.md) | Null pointer dereference in `II_setitem` via re-entrant `__index__` during `array.extend` | 1 | Yes |
| [#142883](gh_142883.md) | Null pointer dereference in `array_repeat` via re-entrant `__index__` during array multiplication | 1 | Yes |
| [#142884](gh_142884.md) | Null pointer dereference in `array.array.tofile` via reentrant writer | 1 | Yes |
| [#142917](gh_142917.md) | memory leak `WARNING: invalid path to external symbolizer` | 1 | — |
| [#142985](gh_142985.md) | Build failure with `--enable-experimental-jit` and ASan: Memory leak in `allocate_executor` during module freezing | 1 | — |
| [#143003](gh_143003.md) | Global buffer overflow in `bytearray_extend` via misleading `__length_hint__` | 1 | Yes |
| [#143004](gh_143004.md) | Use-after-free in `Counter.update` via re-entrant `__add__` | 1 | Yes |
| [#143005](gh_143005.md) | Heap buffer overflow in ctypes array assignment via `__class__` swap | 1 | Yes |
| [#143006](gh_143006.md) | Type confusion in `float_richcompare` via re-entrant `__neg__` | 0 | Yes |
| [#143007](gh_143007.md) | Null pointer dereference in `TextIOWrapper.seek` via re-entrant `__int__` | 1 | Yes |
| [#143008](gh_143008.md) | Null pointer dereference in `TextIOWrapper.truncate` via re-entrant `flush` | 1 | Yes |
| [#143195](gh_143195.md) | Use-after-free in `_Py_strhex_impl` via re-entrant `sep.__len__` in `bytearray.hex` | 1 | Yes |
| [#143196](gh_143196.md) | Heap-buffer-overflow in `json.encoder` indentation cache via re-entrant `__mul__` | 1 | Yes |
| [#143197](gh_143197.md) | Use-after-free in range iterator `__setstate__` via re-entrant `__mul__` | 1 | — |
| [#143198](gh_143198.md) | Null pointer dereference in `_sqlite` cursor cache via re-entrant parameter iterator | 1 | Yes |
| [#143200](gh_143200.md) | Null pointer dereference in `element_[ass_]subscr` via re-entrant calls | 1 | Yes |
| [#143236](gh_143236.md) | Use-after-free in `_PyEval_LoadName` via re-entrant frame locals lookup | 1 | Yes |
| [#143308](gh_143308.md) | Use-after-free in `save_picklebuffer` via re-entrant `buffer_callback` and `__bool__` | 1 | Yes |
| [#143309](gh_143309.md) | Use-after-free in `parse_envlist` via re-entrant `env.keys()` or `env.values()` | 1 | Yes |
| [#143310](gh_143310.md) | Null pointer dereference in `_tkinter` `AsObj` via re-entrant `__str__` | 1 | Yes |
| [#143375](gh_143375.md) | Null pointer dereference in `BufferedWriter.seek` during re-entrant close | 1 | Yes |
| [#143376](gh_143376.md) | Type confusion in `_channelid_shared` via unvalidated `_id` attribute | 1 | Yes |
| [#143377](gh_143377.md) | Heap buffer overflow in `_format_TracebackException` when `TracebackException.format` omits newline | 1 | Yes |
| [#143378](gh_143378.md) | Use-after-free in `_io.BytesIO.writelines` via re-entrant `__buffer__` close | 1 | Yes |
| [#143379](gh_143379.md) | Use-after-free in `s_pack_internal` via re-entrant `__bool__` | 1 | Yes |
| [#143380](gh_143380.md) | Null pointer dereference in `_sqlite` execute via re-entrant sequence length | 1 | Yes |
| [#143424](gh_143424.md) | Deadlock Assertion failure at Python/lock.c:128: PyLockStatus _PyMutex_LockTimed(PyMutex *, PyTime_t, _PyLockFlags): `Assertion '_Py_atomic_load_uint8_relaxed(&m->_bits) & _Py_LOCKED' failed` | 0 | Yes |
| [#143430](gh_143430.md) | Assertion failure at Objects/codeobject.c:1199: 'void advance_with_locations(PyCodeAddressRange *, int *, int *, int *): Assertion `bounds->opaque.lo_next <= bounds->opaque.limit .. ' failed` | 0 | — |
| [#143442](gh_143442.md) | `test_profiling` sometimes times out under TSan | 0 | — |
| [#143543](gh_143543.md) | Use-after-free in `itertools.groupby` via re-entrant key comparison through `__eq__` | 1 | Yes |
| [#143544](gh_143544.md) | Use-after-free in `_json.raise_errmsg` via re-entrant `JSONDecodeError` hook | 1 | Yes |
| [#143545](gh_143545.md) | Use-after-free in lsprof `initContext` via re-entrant external timer `__index__` | 3 | Yes |
| [#143546](gh_143546.md) | Heap buffer overflow in `set_clear_internal` via re-entrant `__eq__` during `set_iand` | 1 | Yes |
| [#143547](gh_143547.md) | Use-after-free when `sys.unraisablehook` fails and falls back to default logger | 1 | Yes |
| [#143635](gh_143635.md) | Use-after-free in `_Py_typing_type_repr` via re-entrant `__origin__` lookup during `GenericAlias` repr | 1 | Yes |
| [#143636](gh_143636.md) | Type confusion in `SimpleNamespace.__replace__` via re-entrant `__new__` | 1 | Yes |
| [#143637](gh_143637.md) | Heap out-of-bound read in `socket.sendmsg` ancillary parser after re-entrant `__index__` clears the control list | 1 | Yes |
| [#143638](gh_143638.md) | Use-after-free in pickle BUILD via re-entrant `__setitem__` | 1 | Yes |
| [#143639](gh_143639.md) | Use-after-free in `_pickle.load_setitem` via re-entrant key `__hash__` | 1 | — |
| [#143640](gh_143640.md) | Termux on Android: Python/parking_lot.c:159:15: error: call to undeclared function 'sem_clockwait' | 0 | — |
| [#143662](gh_143662.md) | Null pointer dereference in `cursor.fetchone` after re-entrant `text_factory` closes connection | 1 | — |
| [#143750](gh_143750.md) | Use OpenSSL instrumented with TSan for TSan tests | 0 | Yes |
| [#143751](gh_143751.md) | JIT: Segfault from setting `UOP_MAX_TRACE_LENGTH` to a large value | 0 | — |
| [#143756](gh_143756.md) | Data races in OpenSSL bindings | 1 | Yes |
| [#144067](gh_144067.md) | Document that it is unsafe to call `curses.initscr` after `curses.setupterm` | 1 | Yes |
| [#144068](gh_144068.md) | Memory leak in _PyJit_TryInitializeTracing when daemon thread exits | 1 | Yes |
| [#144069](gh_144069.md) | Memory leak in _dbm.open (libdb) when file creation fails (ENOENT) | 1 | Yes |
| [#144100](gh_144100.md) | Assertion failed: typeinfo->proto in PyCPointerType_from_param_impl when using deprecated POINTER(str) in argtypes | 0 | Yes |
| [#144128](gh_144128.md) | CPython UaF during index callbacks | 1 | Yes |
| [#144163](gh_144163.md) | Segfault in _testinternalcapi.assemble_code_object with LOAD_CLOSURE | 1 | — |
| [#144169](gh_144169.md) | ast: Segfault in node constructor when passing non-string keyword arguments | 1 | Yes |
| [#144172](gh_144172.md) | tracemalloc: Heap-use-after-free in _Py_IsImmortal when destroying subinterpreters while tracing | 2 | — |
| [#144199](gh_144199.md) | Leak sanitizer errors when `--enable-profiling` is passed to `configure` during build | 0 | — |
| [#144206](gh_144206.md) | fcntl.ioctl raises SystemError: buffer overflow instead of ValueError when mutating undersized buffers | 0 | Yes |
| [#144280](gh_144280.md) | [JIT] Crash (SEGV) in optimizer_symbols.c:696 during symbolic truthiness analysis in Tier 2 uop optimizer | 1 | Yes |
| [#144281](gh_144281.md) | SIGBUS (Invalid Write) in memory_ass_sub via multiprocessing.shared_memory during buffer assignment | 2 | Yes |
| [#144282](gh_144282.md) | "Fatal Python error: _PyEval_EvalFrameDefault: Executing a cache" when prepending CACHE opcodes via code.replace | 0 | — |
| [#144356](gh_144356.md) | Data race in set iterator length_hint under no-gil | 3 | Yes |
| [#144475](gh_144475.md) | heap-buffer-overflow in functools.partial.__repr__() | 1 | Yes |
| [#144567](gh_144567.md) | `heap-use-after-free` running functions from `profiling.sampling` in free-threaded build | 1 | — |
| [#144759](gh_144759.md) | Uninitialized start and multi_line_start Causing Undefined Behavior - Pointer overflow | 1 | Yes |
| [#144833](gh_144833.md) | Use-after-free and type confusion in `newPySSLSocket()` when `SSL_new()` fails | 1 | Yes |
| [#144922](gh_144922.md) | `array.tofile()` crashes due to use-after-free when `write()` callback modifies the array | 1 | — |
| [#144984](gh_144984.md) | NULL deref + Double Py_DECREF in pyexpat ExternalEntityParserCreate() | 1 | Yes |
| [#145036](gh_145036.md) | Possible data race in `list.__sizeof__()` with free-threading build | 2 | Yes |
| [#145199](gh_145199.md) | configure hangs with --with-address-sanitizer on macOS (conftest spins in __asan::InitializeShadowMemory) | 1 | — |
| [#145204](gh_145204.md) | Summary  When running _testembed under LeakSanitizer, test_initconfig_get_api reports a memory leak. | 1 | Yes |
| [#145272](gh_145272.md) | Data race in `func_set_code` | 1 | Yes |
| [#145301](gh_145301.md) | `_hashlib`: Use-After-Free + Double Free in `_hashopenssl.c` `py_hashentry_table_new()` | 0 | Yes |
| [#145933](gh_145933.md) | hmac_digest race condition with openssl 3.0.19 and Python 3.14t | 0 | — |
| [#146011](gh_146011.md) | heap-use-after-free in signaldict_repr: signaldict outlives its parent Context after explicit del | 1 | Yes |
| [#146196](gh_146196.md) | Undefined Behavior in _PyUnicodeWriter_WriteASCIIString: NULL pointer passed to memcpy when len is 0 | 2 | Yes |
| [#146270](gh_146270.md) | `slot.__delete__()` behaves as non-atomic in free-threading | 1 | Yes |
| [#146452](gh_146452.md) | Segfault in _pickle.c:batch_dict_exact when pickling dict with concurrent mutation (free-threading) | 1 | Yes |
| [#147998](gh_147998.md) | Avoid memory leak in `_pop_preserved()` | 1 | Yes |
| [#148286](gh_148286.md) | Various UB warnings found by UBSan | 2 | Yes |
| [#148382](gh_148382.md) | `_decimal::CURRENT_CONTEXT`: UAF via borrowed reference across Python callbacks | 1 | — |
| [#148484](gh_148484.md) | incomplete fix for memory leak in array.array | 1 | Yes |
| [#148625](gh_148625.md) | Crash: use-after-free in `elementiter_next` | 1 | — |
| [#148716](gh_148716.md) | Assertion 'probable_callable != NULL' in optimize_uops when sys.settrace is set and cleared before a type-unstable method call loop crosses the JIT threshold | 0 | — |
| [#148850](gh_148850.md) | Memory sanitizer generates false positives on data returned by os.getrandom() | 1 | Yes |
| [#149142](gh_149142.md) | _decimal: `mpd_context_t::status`/`traps` mutated non-atomically leading to data race | 0 | Yes |
| [#149816](gh_149816.md) | 22 free-threading race conditions | 0 | Yes |
| [#150191](gh_150191.md) | Data race in test_ssl.test_sni_callback_race | 2 | Yes |
| [#150195](gh_150195.md) | Test failures on no-GIL interpreter macOS 26 ARM64 with UBSan | 0 | Yes |
| [#150284](gh_150284.md) | TSan warnings with free-threaded interpreter on macOS 26 arm64 and Clang 22 | 1 | — |
| [#150467](gh_150467.md) | [Asan + msvc] Cpython build failed with error LNK2001: unresolved external symbol on windows | 0 | — |
| [#150536](gh_150536.md) | Importing `readline` leaks memory on macOS | 1 | Yes |
| [#150966](gh_150966.md) | test_profiling: test_run_failed_module_live() fails on AMD64 Arch Linux Asan 3.x | 0 | Yes |
| [#151046](gh_151046.md) | Use-after-free in _Unpickler_ReadIntoFromFile: temporary memoryview passed to readinto() can outlive its buffer | 0 | Yes |
| [#151277](gh_151277.md) | TSan detects a data race when running test_ssl.test_sni_callback_race() on Free Threading | 1 | — |
| [#151403](gh_151403.md) | _posixsubprocess.fork_exec(): use-after-free if an argv item's __fspath__ mutates args | 1 | Yes |
| [#151593](gh_151593.md) | test_abc hangs on TSan Parallel Test on Free Threading | 0 | Yes |
| [#151722](gh_151722.md) | Data race on frozendict reads during construction in the free-threading build | 1 | Yes |
| [#152741](gh_152741.md) | Data race between `sys._current_exceptions()` and a concurrently attaching thread | 3 | Yes |
| [#153014](gh_153014.md) | Data race on the GC debug flag (gc.set_debug/get_debug) in free-threading builds | 1 | Yes |
| [#153201](gh_153201.md) | test_hashlib fails when run on Free Threading with TSAN | 1 | Yes |
| [#153809](gh_153809.md) | asyncio: TaskObj_dealloc leaves a refcount-0 Task GC-tracked, hanging or crashing the free-threaded build | 0 | Yes |
| [#153852](gh_153852.md) | Free-threading data races in CPython: 15 findings (9 new + 6 residual of existing FT work) | 1 | Yes |
| [#153908](gh_153908.md) | tsan-006: itertoolsmodule.c: count.__repr__ plain-reads cnt | 1 | Yes |
| [#153928](gh_153928.md) | thread safety issues in unicodeobject.c | 2 | Yes |
| [#153981](gh_153981.md) | itertoolsmodule: free-threading use after free bug in counting slow mode | 2 | Yes |
| [#154043](gh_154043.md) | segfault in ga_iternext: sharing a types.GenericAlias iterator across threads double-frees under free-threading | 1 | Yes |
| [#154044](gh_154044.md) | Data race + leak: descr_get_qualname lazily caches d_qualname without synchronization (free-threading) | 1 | Yes |
| [#154130](gh_154130.md) | Sharing a dict iterator across threads double-DECREFs di_dict under free-threading | 2 | — |
| [#154189](gh_154189.md) | use-after-free: functools partial | 1 | Yes |
| [#154524](gh_154524.md) | Data race: ctypes `PyCData_NewGetBuffer` reads `b_ptr` without the critical section `_ctypes_resize` holds | 2 | — |
| [#154535](gh_154535.md) | Sharing a `contextvars.Context` iterator across threads crashes (HAMT iterator cursor corruption) under free-threading | 1 | Yes |
| [#154667](gh_154667.md) | `zipfile`: Inconsistent and insufficient date_time validation and handling across `ZipInfo` methods | 0 | Yes |
| [#154756](gh_154756.md) | Data race in list.sort() on no-gil build | 1 | Yes |
| [#154821](gh_154821.md) | Race on func_get_name/func_set_name under free threading | 1 | Yes |
| [#154822](gh_154822.md) | Free-threading: data race on `interp->threads.head` in `handle_thread_shutdown_exception` (unlocked `assert` before `_PyEval_StopTheWorld`) | 1 | Yes |
| [#156762](gh_156762.md) | `_operator`: `methodcaller_clear` has the wrong signature for the `tp_clear` slot (returns `void`, not `int`) | 1 | Yes |
| [#54726](gh_54726.md) | test_concurrent_futures crashes with "--with-pydebug" on RHEL5 with "Fatal Python error: Invalid thread state for this thread" | 0 | Refs only |
| [#57894](gh_57894.md) | argparse update help msg  for % signs | 0 | Refs only |
| [#65128](gh_65128.md) | Undefined behavior flagged by Clang 3.4 (Python 3.4-RC3) | 2 | Refs only |
| [#66234](gh_66234.md) | Fatal error in dbm.gdbm | 0 | Yes |
| [#71757](gh_71757.md) | Avoid memcpy(. . ., NULL, 0) etc calls | 2 | Refs only |
| [#72111](gh_72111.md) | ensurepip raises TypeError after pip uninstall | 0 | — |
| [#72174](gh_72174.md) | obmalloc's 8-byte alignment causes undefined behavior | 2 | Yes |
| [#73069](gh_73069.md) | Python 3.5.2 crashers (from PyPy) | 0 | Yes |
| [#73331](gh_73331.md) | failing overflow checks in replace_* | 0 | Refs only |
| [#75554](gh_75554.md) | demoting floating float values to unrepresentable types is undefined behavior | 1 | Yes |
| [#77756](gh_77756.md) | Python relies on C undefined behavior float-cast-overflow | 0 | — |
| [#77808](gh_77808.md) | test-complex of test_numeric_tower.test_complex() crashes intermittently on Ubuntu buildbots | 0 | — |
| [#77813](gh_77813.md) | undefined behaviour: signed integer overflow in threadmodule.c | 2 | Yes |
| [#79374](gh_79374.md) | Off by one error in peephole call to find_op on case RETURN_VALUE | 0 | Yes |
| [#80434](gh_80434.md) | Use after free in ctypes test suite | 0 | Yes |
| [#81319](gh_81319.md) | PEP 590 method_vectorcall calls memcpy with NULL src | 1 | Yes |
| [#83870](gh_83870.md) | struct and memoryview tests rely on undefined behavior (as revealed by clang 9) | 3 | Yes |
| [#83957](gh_83957.md) | PyContextVar_Get(): crash due to race condition in updating tstate->id | 0 | Yes |
| [#85863](gh_85863.md) | Heap buffer overflow in the parser | 1 | Yes |
| [#86434](gh_86434.md) | ./configure failing when --with-memory-sanitizer specified | 1 | Yes |
| [#86863](gh_86863.md) | 3.8.7rc1 regression: 'free(): invalid pointer' after running backports-zoneinfo test suite | 1 | — |
| [#88350](gh_88350.md) | crash on windows invoking flake8 | 2 | Yes |
| [#89359](gh_89359.md) | macOS. ./configure --with-address-sanitizer; make test; cause test case crash. | 1 | Yes |
| [#89363](gh_89363.md) | Address Sanitizer: libasan dead lock in pthread_create() (test_multiprocessing_fork.test_get() hangs) | 0 | Yes |
| [#89391](gh_89391.md) | Stack buffer overflow in parsing J1939 network address | 0 | Yes |
| [#89571](gh_89571.md) | [fuzzer] Weird input with continuation and newlines causes null deref in parser | 1 | Yes |
| [#89657](gh_89657.md) | [fuzzer] Parser null deref with continuation characters and generator parenthesis error | 1 | Yes |
| [#89737](gh_89737.md) | Warning: ‘print_escape’ defined but not used | 0 | Yes |
| [#93619](gh_93619.md) | Linking error when building 3.11 beta on mips64le | 0 | — |
| [#93981](gh_93981.md) | Address Sanitizer: some test function of test.test_concurrent_futures  fail | 1 | — |
| [#94064](gh_94064.md) | ASAN : Memory leak found in python3.9.9 regrtest | 3 | — |
| [#94404](gh_94404.md) | makesetup can fail on macOS and uses wrong CFLAGS | 0 | Yes |
| [#95635](gh_95635.md) | make test fails; executable works; runtime error in background | 3 | — |
| [#96569](gh_96569.md) | undefined behavior: tstate->datastack_top == NULL | 1 | Yes |
| [#96572](gh_96572.md) | Use after free in 3.11 | 2 | Yes |
| [#96678](gh_96678.md) | Undefined behaviour in `main` and 3.11 | 3 | Yes |
| [#96714](gh_96714.md) | Wild pointer detected with ASAN during source build | 1 | — |
| [#96735](gh_96735.md) | Undefined behavior in `struct.unpack` | 1 | — |
| [#98249](gh_98249.md) | /bin/sh: 1: python: not found | 0 | — |
| [#99974](gh_99974.md) | Leak 21~42 bits of heap data in python 3.12 by exploiting the code object co_positions iterator | 0 | — |
| [#99975](gh_99975.md) | Out of bound read of two bytes in 3.10 if code object `co_lnotab = b'\0'` | 0 | — |
