import functools

# Evil key: __hash__/__eq__ reenter and clear/mutate the SAME lru cache mid-lookup.
CLEAR = [True]

@functools.lru_cache(maxsize=4)
def f(x):
    return ("R", x)

class Evil:
    def __init__(self, n):
        self.n = n
    def __hash__(self):
        if CLEAR[0]:
            f.cache_clear()
        return 7  # collide everything -> forces __eq__ probing
    def __eq__(self, other):
        if CLEAR[0]:
            f.cache_clear()
        return isinstance(other, Evil) and other.n == self.n

# populate a few entries (no clearing while populating)
CLEAR[0] = False
for i in range(4):
    f(Evil(i))
CLEAR[0] = True

# now every hash/eq clears the cache mid-op
for i in range(4):
    try:
        f(Evil(i))
    except Exception as e:
        pass
    f(Evil(100 + i))
print("t_lru_clear done")
