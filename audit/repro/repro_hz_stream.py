import sys, io, codecs
which = sys.argv[1]
if which == "textiowrapper":
    # Truncated hz stream ending right after '~' read via text layer at EOF.
    io.TextIOWrapper(io.BytesIO(b'~'), encoding='hz').read()
elif which == "streamreader":
    codecs.getreader('hz')(io.BytesIO(b'~')).read()
elif which == "iterdecode":
    list(codecs.iterdecode([b'~'], 'hz'))
print("completed without abort", flush=True)
