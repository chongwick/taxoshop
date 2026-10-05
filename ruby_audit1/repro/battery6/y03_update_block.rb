h={}; (0...6).each{|i| h[i]=i}; $h=h
h.update({0=>9,1=>9,2=>9}) { |k,o,n| $h.clear; o } rescue (puts "raised")
puts "y03 ok"
