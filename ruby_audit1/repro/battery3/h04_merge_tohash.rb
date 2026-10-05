h = {}; 3000.times{|i| h[i]=i}; $h=h
o = Object.new; def o.to_hash; $h.clear; {a:1}; end
h.merge(o) rescue (puts "raised")
puts "h04 ok"
