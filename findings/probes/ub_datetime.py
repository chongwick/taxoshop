import datetime as dt
tries = [
  lambda: dt.timedelta(days=999999999) * (2**62),
  lambda: dt.timedelta(seconds=(1<<62)) + dt.timedelta(seconds=(1<<62)),
  lambda: dt.date.max + dt.timedelta(days=(1<<62)),
  lambda: dt.datetime(1,1,1) - dt.timedelta(days=(1<<62)),
  lambda: dt.timedelta(microseconds=(1<<63)-1) * 1000000,
  lambda: dt.timedelta.max // dt.timedelta(microseconds=1),
]
for i,f in enumerate(tries):
    try: f()
    except Exception as e: pass
print("OK ub_datetime")
