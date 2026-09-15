s = "A"*4000
s.each_byte { s.clear } rescue (puts "raised")
puts "t08 ok"
