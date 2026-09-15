a = [0]*4000
a.fill { |i| a.clear if i==0; i } rescue (puts "raised")
puts "t12 ok"
