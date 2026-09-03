# str.translate with a mapping whose __getitem__ mutates... str is immutable, but
# check the C translate path with an evil mapping returning huge/odd values.
class M:
    def __getitem__(self, k):
        return "X" * 100000
try:
    print(len("abcabc".translate(M())))
except Exception as e:
    print("exc", type(e).__name__)
print("OK sweep2_translate")
