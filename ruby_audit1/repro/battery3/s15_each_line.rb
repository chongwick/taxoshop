s = ("a\n"*4000); $s=s
s.each_line { $s.clear } rescue (puts "raised")
puts "s15 ok"
