# concurrent SubElement (element_resize -> PyMem_Realloc frees children[]) vs root[i]
# (element_getitem reads children[index]) => UAF / data race on Element.extra->children
import xml.etree.ElementTree as ET, threading
root = ET.Element("r")
for _ in range(64):
    ET.SubElement(root, "c")
stop = False
def grower():
    while not stop:
        for _ in range(64):
            ET.SubElement(root, "c")      # realloc children buffer
        del root[64:]                     # shrink back so indices stay valid-ish
def reader():
    while not stop:
        n = len(root)
        for i in range(min(n, 64)):
            try:
                x = root[i]               # reads children[index], Py_NewRef
                _ = x.tag
            except IndexError:
                pass
            except Exception:
                pass
r = threading.Thread(target=reader)
g = threading.Thread(target=grower)
r.start(); g.start()
import time
# bounded run
def stopper():
    import time as _t; _t.sleep(8)
s = threading.Thread(target=stopper); s.start()
s.join(); stop = True
g.join(); r.join()
print("et_getitem done")
