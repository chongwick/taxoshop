import itertools as it, threading, sys
def hammer(make, n=4, iters=200000):
    obj = make()
    def w():
        for _ in range(iters):
            try: next(obj)
            except StopIteration: break
            except Exception: break
    ts=[threading.Thread(target=w) for _ in range(n)]
    for t in ts: t.start()
    for t in ts: t.join()

name = sys.argv[1]
makers = {
 "cycle":  lambda: it.cycle([1,2,3,4,5]),
 "chain":  lambda: it.chain(range(100000), range(100000)),
 "accumulate": lambda: it.accumulate(range(1000000)),
 "islice": lambda: it.islice(it.count(), 1000000),
 "repeat": lambda: it.repeat(7),
 "starmap": lambda: it.starmap(lambda a,b:a+b, zip(range(1000000),range(1000000))),
 "compress": lambda: it.compress(range(1000000),[1,0,1]*400000),
 "dropwhile": lambda: it.dropwhile(lambda x:x<0, range(1000000)),
 "takewhile": lambda: it.takewhile(lambda x:x>=0, range(1000000)),
 "filterfalse": lambda: it.filterfalse(lambda x:False, range(1000000)),
 "zip_longest": lambda: it.zip_longest(range(500000),range(600000)),
 "product": lambda: it.product(range(1000),range(1000)),
 "permutations": lambda: it.permutations(range(50),3),
 "combinations": lambda: it.combinations(range(200),3),
 "count":  lambda: it.count(),
 "pairwise": lambda: it.pairwise(range(1000000)),
 "groupby": lambda: it.groupby(range(1000000)),
 "batched": lambda: it.batched(range(1000000), 3),
}
hammer(makers[name])
print(name, "done")
