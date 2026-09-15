a = (1..3000).to_a
a.keep_if { |x| a.clear if x==1; true } rescue (puts "raised")
puts "u18 ok"
