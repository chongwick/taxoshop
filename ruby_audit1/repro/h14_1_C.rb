# Does the simplest "C*" byte directive also trip it?
s = "A" * 400
s.unpack("C*") { s.clear }
