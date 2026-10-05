h={}; (0...6).each{|i| h[i]=i}; $h=h
h.each_with_index { |(k,v),idx| 50.times{|i| $h["x#{i}"]=i} if idx==0 } rescue (puts "raised")
puts "y07 ok"
