class EvilMap:
    def __getitem__(self, k):
        return "z"*100
print("{a}{b}{c}".format_map(EvilMap()))
print("format_map ok")
