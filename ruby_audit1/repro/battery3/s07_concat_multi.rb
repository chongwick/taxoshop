s = "x"*4000; $s=s
o = Object.new; def o.to_str; $s.replace("z"); "y"; end
s.concat("a", o, "b") rescue (puts "raised")
puts "s07 ok"
