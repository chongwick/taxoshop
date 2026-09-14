import datetime
class EI(int): pass
try:
    d = datetime.datetime(2020, EI(1), EI(1))
    print(d)
except Exception as e:
    print("exc", type(e).__name__)
# timedelta with evil float
class F:
    def __float__(self):
        return 1e300
try:
    print(datetime.timedelta(seconds=F()))
except Exception as e:
    print("exc", type(e).__name__)
print("datetime ok")
