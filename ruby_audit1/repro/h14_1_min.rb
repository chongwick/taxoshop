# Minimal: unpack with block, block clears the source string.
s = "C" * 4000
s.unpack("L*") { s.clear }
