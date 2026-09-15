# unpack1 with block path
s = "Z" * 4000
s.unpack1("L*") { s.clear }
puts "no-crash"
