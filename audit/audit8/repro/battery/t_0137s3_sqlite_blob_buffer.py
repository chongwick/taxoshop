# 0137 S3/S1/S9 style: PEP-688 __buffer__ that tears down self->resource before the native op.
# sqlite Blob.write(EvilBuf) where __buffer__ closes the blob/connection.
import sqlite3

class EvilBuf:
    def __init__(self, cb): self.cb = cb
    def __buffer__(self, flags):
        self.cb()
        return memoryview(b"Z")

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE t(b blob)")
con.execute("INSERT INTO t(b) VALUES (zeroblob(16))")
con.commit()
rowid = con.execute("SELECT rowid FROM t").fetchone()[0]

# A: __buffer__ closes the blob
blob = con.blobopen("t", "b", rowid)
def close_blob():
    blob.close()
try:
    blob.write(EvilBuf(close_blob))
    print("A wrote (no crash)")
except Exception as ex:
    print("A raised:", type(ex).__name__, ex)

# B: __buffer__ closes the connection (frees blob under it)
con2 = sqlite3.connect(":memory:")
con2.execute("CREATE TABLE t(b blob)")
con2.execute("INSERT INTO t(b) VALUES (zeroblob(16))")
con2.commit()
rid2 = con2.execute("SELECT rowid FROM t").fetchone()[0]
blob2 = con2.blobopen("t", "b", rid2)
def close_con():
    con2.close()
try:
    blob2.write(EvilBuf(close_con))
    print("B wrote (no crash)")
except Exception as ex:
    print("B raised:", type(ex).__name__, ex)

# C: hashlib update with __buffer__ that re-enters update on same object
import hashlib
h = hashlib.sha256()
def reenter():
    h.update(b"reentrant")
try:
    h.update(EvilBuf(reenter))
    print("C hashed:", h.hexdigest()[:8])
except Exception as ex:
    print("C raised:", type(ex).__name__, ex)
print("0137s3 done")
