h={}; (0...3000).each{|i| h[i]=i}; $h=h
k=Object.new; def k.hash; $h.clear; 1; end; def k.eql?(o);false;end
h.slice(0,1,k) rescue (puts "raised")
puts "y09 ok"
