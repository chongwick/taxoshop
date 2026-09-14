import re, threading
m=re.match(r"(a)(b)(c)(d)","abcd")
def f():
    for _ in range(200000):
        try: _=m.group(1); _=m[2]; _=m.groups(); _=m.span(3)
        except Exception: pass
ts=[threading.Thread(target=f) for _ in range(6)]
for t in ts:t.start()
for t in ts:t.join()
print("re_match done")
