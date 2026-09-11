import codecs
d = codecs.getincrementaldecoder('hz')()
d.decode(b'~', False)   # lone '~' buffered as pending
d.decode(b'', True)     # tight 1-byte re-decode -> INBYTE2 over-read
