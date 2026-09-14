# wf0080 Site 3: ElementPath predicate matching, evil tag __eq__ clears parent
import xml.etree.ElementTree as ET
class EvilTag(str):
    def __eq__(self, other):
        parent.clear()
        return False
    __hash__ = str.__hash__
parent = ET.Element("root")
for i in range(6):
    c = ET.SubElement(parent, EvilTag("child%d" % i))
try:
    r = parent.find("target")
    print("find ->", r)
except Exception as e:
    print("find", type(e).__name__, e)
print("elementtree done")
