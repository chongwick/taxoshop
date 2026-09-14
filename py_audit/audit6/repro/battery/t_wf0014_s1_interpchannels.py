# wf0014 Site 1: cross-interpreter channel buffer aliases sender's exporter
import _interpchannels as chan
import _interpreters as interp
cid = chan.create()
code = '''
import _interpchannels as chan
ba = bytearray(b"ABCDEFGH" * 4)
mv = memoryview(ba)
chan.send({cid}, mv, blocking=False)
'''.format(cid=cid)
sub = interp.create()
try:
    interp.run_string(sub, code)
except Exception as e:
    print("subinterp run:", type(e).__name__, e)
try:
    obj, unbound = chan.recv(cid)
    print("recv type:", type(obj).__name__)
    interp.destroy(sub)          # frees sender's exporter bytearray
    import gc; gc.collect()
    print("byte:", bytes(obj[:8]))   # read aliased freed buffer
except Exception as e:
    print("recv:", type(e).__name__, e)
print("interpchannels done")
