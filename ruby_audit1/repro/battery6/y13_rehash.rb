h={}; (0...3000).each{|i| h[i]=i}; $h=h
bad=Object.new; def bad.hash; $h.clear; 5; end; def bad.eql?(o);false;end
h[bad]=1
h.rehash rescue (puts "raised")
puts "y13 ok"
