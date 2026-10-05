s = "x"*4000; $s=s
w = Object.new; def w.to_int; $s.clear; 8000; end
s.ljust(w, "-") rescue (puts "raised")
puts "s01 ok"
