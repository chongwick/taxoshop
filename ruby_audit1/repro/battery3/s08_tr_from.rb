s = "x"*4000; $s=s
o = Object.new; def o.to_str; $s.clear; "x"; end
s.tr(o, "y") rescue (puts "raised")
puts "s08 ok"
