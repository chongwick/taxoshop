a = (1..3000).to_a
a.select! { |x| a.clear if x==1; true } rescue (puts "raised")
puts "u16 ok"
