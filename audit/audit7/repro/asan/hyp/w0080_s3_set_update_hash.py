# 0080 S3: set update rehash during __hash__ frees table
so = set()
fired = [False]
junk = []
class Evil:
    def __init__(self, n): self.n = n
    def __hash__(self):
        if not fired[0]:
            fired[0] = True
            so.clear()
            for _ in range(50):
                junk.append(bytes(4096))
        return 12345
    def __eq__(self, other):
        return self is other
so |= set(range(200))
try:
    so.update([Evil(i) for i in range(50)])
except Exception as e:
    print("exc(update)", type(e).__name__, e)
print("survived s3")
