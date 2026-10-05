h = {}; 3000.times{|i| h[i]=i}; $h=h
k = Object.new; def k.hash; $h.clear; 1; end; def k.eql?(o); false; end
h.values_at(k, 0, 1) rescue (puts "raised")
puts "h02 ok"
