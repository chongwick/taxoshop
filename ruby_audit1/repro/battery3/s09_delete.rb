s = "x"*4000; $s=s
o = Object.new; def o.to_str; $s.clear; "x"; end
s.delete(o) rescue (puts "raised")
puts "s09 ok"
