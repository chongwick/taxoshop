s = "x"*4000; $s=s
i = Object.new; def i.to_int; $s.clear; 10; end
s[i] = "Q" rescue (puts "raised")
puts "s12 ok"
