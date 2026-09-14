# wf0080 Site 4: future_schedule_callbacks with evil loop mutating callbacks
import asyncio
class EvilLoop:
    def get_debug(self): return False
    def call_soon(self, cb, *a, context=None):
        # mutate/clear the future's callbacks & drop refs during dispatch
        try: fut.remove_done_callback(cb2)
        except Exception: pass
        try: fut._callbacks.clear()
        except Exception: pass
        return None
loop = EvilLoop()
fut = asyncio.Future(loop=loop)
def cb1(f): pass
def cb2(f): pass
fut.add_done_callback(cb1)
fut.add_done_callback(cb2)
try:
    fut.set_result(42)   # triggers __schedule_callbacks
    print("asyncio ok")
except Exception as e:
    print("asyncio", type(e).__name__, e)
print("asyncio done")
