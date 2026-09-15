a = (1..3000).to_a
a.reject! { |x| a.clear if x==1; false } rescue (puts "raised")
puts "u15 ok"
