import itertools
tries = [
  lambda: next(itertools.islice(itertools.count((1<<63)-1), 1)),
  lambda: next(itertools.count((1<<63)-2, (1<<63)-1).__iter__()),
  lambda: list(itertools.islice(itertools.count(0, (1<<62)), 3)),
  lambda: next(iter(itertools.repeat(0, (1<<63)))),
]
c = itertools.count((1<<63)-3)
for f in tries:
    try: f()
    except Exception: pass
try:
    for _ in range(5): next(c)   # overflow the C ssize_t counter
except Exception: pass
print("OK ub_itertools")
