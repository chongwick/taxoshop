import xml.etree.ElementTree as ET
class EvilTag(str):
    hits = 0
    def __eq__(self, other):
        EvilTag.hits += 1
        parent.clear()
        return False
    __hash__ = str.__hash__
parent = ET.Element("root")
for i in range(6):
    ET.SubElement(parent, EvilTag("kid"))
try:
    r = parent.findall("kid")
    print("findall ->", r, "hits", EvilTag.hits)
except Exception as e:
    print("findall", type(e).__name__, e)
print("et findall done")
