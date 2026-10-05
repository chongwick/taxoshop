s = "x"*4000; $s=s
i = Object.new; def i.to_int; $s.clear; 100; end
s.insert(i, "ABCDEFGH") rescue (puts "raised")
puts "s05 ok"
