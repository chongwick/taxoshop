s = "x"*4000; $s=s
o = Object.new; def o.to_str; $s.clear; "y"; end
s.partition(o) rescue (puts "raised")
puts "s17 ok"
