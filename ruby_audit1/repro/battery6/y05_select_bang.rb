h={}; (0...6).each{|i| h[i]=i}; $h=h
h.select! { |k,v| 50.times{|i| $h["x#{i}"]=i} if k==0; true } rescue (puts "raised")
puts "y05 ok"
