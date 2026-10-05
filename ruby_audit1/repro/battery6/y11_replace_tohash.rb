h={}; (0...3000).each{|i| h[i]=i}; $h=h
o=Object.new; def o.to_hash; $h.clear; {a:1}; end
h.replace(o) rescue (puts "raised")
puts "y11 ok"
