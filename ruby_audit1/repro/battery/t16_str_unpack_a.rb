s = "A"*4000
s.unpack("a1000a1000a1000a1000") { s.clear } rescue (puts "raised")
puts "t16 ok"
