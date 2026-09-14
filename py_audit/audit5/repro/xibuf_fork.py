import os, sys, io, contextlib
import _interpreters                       # register memoryview as shareable
import _interpqueues as Q, _testcapi
buf = bytearray(b"ABCD" * 8)

def trial(n):
    qid = Q.create(10, 2, 0)
    Q.put(qid, memoryview(buf), 2, 0)
    _testcapi.set_nomemory(n, n + 1)
    try:
        Q.get(qid)
    except BaseException:
        pass
    _testcapi.remove_mem_hooks()

results = {}
for n in range(0, 45):
    # flush parent stdout so child doesn't duplicate buffer
    sys.stdout.flush()
    pid = os.fork()
    if pid == 0:
        # child: redirect stdout to devnull; leave stderr for ASan report
        os.close(1)
        os.open(os.devnull, os.O_WRONLY)
        trial(n)
        os._exit(0)
    _, status = os.waitpid(pid, 0)
    if os.WIFSIGNALED(status):
        results[n] = "CRASH sig%d" % os.WTERMSIG(status)
    elif os.WEXITSTATUS(status) != 0:
        results[n] = "exit%d" % os.WEXITSTATUS(status)
    else:
        results[n] = "ok"

for n in sorted(results):
    print(n, results[n])
crashes = [n for n,v in results.items() if v.startswith("CRASH") or v.startswith("exit")]
print("CRASH/abort at N =", crashes)
