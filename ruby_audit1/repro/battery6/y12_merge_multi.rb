h={}; (0...3000).each{|i| h[i]=i}; $h=h
o=Object.new; def o.to_hash; $h.clear; {a:1}; end
h.merge({z:1}, o) rescue (puts "raised")
puts "y12 ok"
