a = (1..3000).to_a
a.uniq { |x| a.clear if x==1; x } rescue (puts "raised")
puts "u07 ok"
