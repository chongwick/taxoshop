# Tightest: 2 elements is enough. Block fires on elem 1, frees buffer; elem 2 reads freed s.
s = "\x00" * 32        # 8 x uint32; heap-allocated (>23 bytes)
s.unpack("N*") { s.clear }
