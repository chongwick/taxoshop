# 0014 S3: DirEntry.stat/is_dir after ScandirIterator closed
import os
it = os.scandir(".")
e = next(it)
it.close()
for meth in ("stat", "is_dir", "is_file"):
    try:
        print(meth, getattr(e, meth)())
    except Exception as ex:
        print(meth, "exc", type(ex).__name__, ex)
# also GC the iterator entirely
del it
e2 = None
it2 = os.scandir(".")
e2 = next(it2)
del it2
import gc; gc.collect()
try:
    print("post-gc stat", e2.stat())
except Exception as ex:
    print("post-gc exc", type(ex).__name__, ex)
print("survived s3")
