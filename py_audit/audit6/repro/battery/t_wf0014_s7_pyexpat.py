# wf0014 Site 7: pyexpat subparser outlives parent
import xml.parsers.expat as expat
child_holder = {}
def ext_ref(context, base, sysid, pubid):
    sub = parent.ExternalEntityParserCreate(context)
    child_holder["sub"] = sub
    sub.Parse("<sub/>", True)
    return 1
parent = expat.ParserCreate()
parent.ExternalEntityRefHandler = ext_ref
doc = ('<?xml version="1.0"?>'
       '<!DOCTYPE r [<!ENTITY e SYSTEM "x">]>'
       '<r>&e;</r>')
try:
    parent.Parse(doc, True)
except Exception as e:
    print("parse:", type(e).__name__, e)
del parent
import gc; gc.collect()
sub = child_holder.get("sub")
if sub is not None:
    try:
        sub.Parse("<more/>", True)   # use child after parent freed
        print("child parse ok")
    except Exception as e:
        print("child parse:", type(e).__name__, e)
print("pyexpat done")
