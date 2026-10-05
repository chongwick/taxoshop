s = "x"*4000; $s=s
o = Object.new; def o.to_str; $s.clear; "x"; end
s.squeeze(o) rescue (puts "raised")
puts "s10 ok"
