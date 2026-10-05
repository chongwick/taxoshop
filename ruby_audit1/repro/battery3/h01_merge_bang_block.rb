h = {}; 3000.times{|i| h[i]=i}; $h=h
h.merge!({0=>9}) { |k,o,n| $h.clear; o } rescue (puts "raised")
puts "h01 ok"
