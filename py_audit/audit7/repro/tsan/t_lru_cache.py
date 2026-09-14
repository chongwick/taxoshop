import functools, threading
@functools.lru_cache(maxsize=128)
def fib(n): return n if n<2 else fib(n-1)+fib(n-2)
def f():
    import random
    for _ in range(100000): fib(random.randint(0,200))
ts=[threading.Thread(target=f) for _ in range(6)]
for t in ts:t.start()
for t in ts:t.join()
print("lru_cache done")
