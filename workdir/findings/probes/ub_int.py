tries = [
  lambda: (1).to_bytes((1<<62), 'big'),
  lambda: int.from_bytes(b'\xff'*8, 'big', signed=True) << (1<<40),
  lambda: (-1) << (1<<40),
  lambda: (2**100) ** (2**40),
  lambda: (1<<63).__index__(),
  lambda: round(2**63, -5),
  lambda: (10**1000) // (10**500),
]
for f in tries:
    try: f()
    except Exception: pass
print("OK ub_int")
