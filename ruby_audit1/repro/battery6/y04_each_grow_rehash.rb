h={}; (0...6).each{|i| h[i]=i}; $h=h   # ar_table
h.each { |k,v| 50.times{|i| $h["x#{i}"]=i} } rescue (puts "raised")   # force ar->st mid-iter
puts "y04 ok"
