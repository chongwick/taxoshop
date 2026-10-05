s = "x"*4000; $s=s
pad = Object.new; def pad.to_str; $s.clear; "-"; end
s.ljust(8000, pad) rescue (puts "raised")
puts "s02 ok"
