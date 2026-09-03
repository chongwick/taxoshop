tries = [
  lambda: float('inf').__trunc__(),
  lambda: int(float('1e400')) if False else int(1e308)*10**40,
  lambda: (1e308).hex(),
  lambda: float.fromhex('0x1.fffffffffffffp+1023') * 2,
  lambda: (2.0**1023).__round__(-400),
  lambda: complex(1e308, 1e308) ** 3,
]
for f in tries:
    try: f()
    except Exception: pass
print("OK ub_float")
