s = "x"*4000; $s=s
i = Object.new; def i.to_int; $s.clear; 10; end
s.byteslice(i, 100) rescue (puts "raised")
puts "s14 ok"
