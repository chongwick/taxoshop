# charmap decode with an evil mapping that mutates
class EvilMap:
    def __getitem__(self, k):
        return "　"
import codecs
data = bytes(range(256))*10
try:
    out = codecs.charmap_decode(data, "strict", EvilMap())
    print("charmap len", len(out[0]))
except Exception as e:
    print("exc", type(e).__name__)
print("charmap_decode ok")
