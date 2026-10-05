s = "x"*4000; $s=s
i = Object.new; def i.to_int; $s.clear; 10; end
s.slice!(i, 5) rescue (puts "raised")
puts "s13 ok"
