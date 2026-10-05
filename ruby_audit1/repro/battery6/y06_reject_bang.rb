h={}; (0...6).each{|i| h[i]=i}; $h=h
h.reject! { |k,v| 50.times{|i| $h["x#{i}"]=i} if k==0; false } rescue (puts "raised")
puts "y06 ok"
