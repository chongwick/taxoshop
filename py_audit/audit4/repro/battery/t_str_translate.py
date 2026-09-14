class EvilMap:
    def __getitem__(self, k):
        return 0x41
s = "abcdefg"*100
print(len(s.translate(EvilMap())))
print("str_translate ok")
