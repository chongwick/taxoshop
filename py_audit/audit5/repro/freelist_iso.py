import sys
mode = sys.argv[1] if len(sys.argv) > 1 else "queue_empty"
import _testcapi

if mode == "queue_empty":
    # get() on an empty queue under first-allocation failure
    import _interpqueues as Q
    qid = Q.create(0, 2, 0)
    _testcapi.set_nomemory(0, 1)
    try:
        Q.get(qid)
    except BaseException as e:
        _testcapi.remove_mem_hooks()
        print("queue_empty ->", type(e).__name__)
    finally:
        _testcapi.remove_mem_hooks()

elif mode == "tuple_only":
    # pure tuple churn (exercise freelist) then fail one allocation
    for _ in range(1000):
        t = tuple(range(3)); del t
    _testcapi.set_nomemory(0, 1)
    try:
        t = (1, 2, 3)
    except BaseException as e:
        _testcapi.remove_mem_hooks()
        print("tuple_only ->", type(e).__name__)
    finally:
        _testcapi.remove_mem_hooks()

elif mode == "import_oom":
    # trigger an import under first-allocation failure (no queues at all)
    _testcapi.set_nomemory(0, 1)
    try:
        import textwrap  # arbitrary not-yet-imported module
    except BaseException as e:
        _testcapi.remove_mem_hooks()
        print("import_oom ->", type(e).__name__)
    finally:
        _testcapi.remove_mem_hooks()

print("done", mode)
