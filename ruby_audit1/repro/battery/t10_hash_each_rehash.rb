h = {a:1}
h.each { 3000.times{|i| h[i]=i} } rescue (puts "raised")
puts "t10 ok"
