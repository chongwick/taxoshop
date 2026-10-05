s = "a,"*4000; $s=s
o = Object.new; def o.to_str; $s.clear; ","; end
s.split(o) rescue (puts "raised")
puts "s16 ok"
