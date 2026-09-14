import sqlite3


con = sqlite3.connect(":memory:")
con.execute("create table t (id integer primary key, data blob)")
con.execute("insert into t(data) values (zeroblob(4))")
blob = con.blobopen("t", "data", 1, readonly=False)


class ClosingIndex:
    def __index__(self):
        blob.close()
        return 0


blob[ClosingIndex()]
