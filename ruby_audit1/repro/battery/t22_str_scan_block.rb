s = "a"*4000
s.scan(/a/) { s.clear } rescue (puts "raised")
puts "t22 ok"
