s = "A"*4000
s.each_char { s.clear } rescue (puts "raised")
puts "t09 ok"
