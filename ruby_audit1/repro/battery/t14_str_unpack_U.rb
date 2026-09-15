s = ([0x41]*4000).pack("U*")
s.unpack("U*") { s.clear } rescue (puts "raised")
puts "t14 ok"
