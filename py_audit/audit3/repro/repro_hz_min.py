import codecs


d = codecs.getincrementaldecoder("hz")()
d.decode(b"~", False)
d.decode(b"", False)
