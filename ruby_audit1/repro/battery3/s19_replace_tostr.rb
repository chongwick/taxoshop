s = "x"*4000; $s=s
o = Object.new; def o.to_str; $s.clear; "y"*10; end
s.replace(o) rescue (puts "raised")
puts "s19 ok"
