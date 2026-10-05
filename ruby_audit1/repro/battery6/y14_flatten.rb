h={}; (0...3000).each{|i| h[i]=i}
h.flatten rescue (puts "raised")
puts "y14 ok"
