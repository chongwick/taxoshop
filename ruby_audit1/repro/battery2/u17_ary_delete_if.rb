a = (1..3000).to_a
a.delete_if { |x| a.clear if x==1; false } rescue (puts "raised")
puts "u17 ok"
