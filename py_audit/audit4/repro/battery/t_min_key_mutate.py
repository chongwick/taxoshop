data = list(range(100))
def key(x):
    data.clear()
    return -x
try:
    m = min(data, key=key)
    print("min", m)
except Exception as e:
    print("exc", type(e).__name__)
print("min ok")
