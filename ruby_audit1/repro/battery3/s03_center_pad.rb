s = "x"*4000; $s=s
pad = Object.new; def pad.to_str; $s.clear; "-"; end
s.center(9000, pad) rescue (puts "raised")
puts "s03 ok"
