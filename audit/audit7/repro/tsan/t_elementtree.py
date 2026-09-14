import xml.etree.ElementTree as ET, threading
root=ET.Element("r")
def a():
    for i in range(100000):
        ET.SubElement(root,"c").text="x"
def r():
    for _ in range(100000):
        try: _=len(root); _=list(root)[:2]; _=root.find("c")
        except Exception: pass
ts=[threading.Thread(target=a),threading.Thread(target=r),threading.Thread(target=a),threading.Thread(target=r)]
for t in ts:t.start()
for t in ts:t.join()
print("elementtree done")
