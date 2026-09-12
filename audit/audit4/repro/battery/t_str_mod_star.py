class EvilWidth:
    def __index__(self):
        return 5
class EvilStr:
    def __str__(self):
        return "x"*10000
print(len("%*s|%s" % (EvilWidth(), EvilStr(), EvilStr())))
print("str_mod ok")
