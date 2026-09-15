a = (1..4000).to_a
a.each_slice(2) { a.clear } rescue (puts "raised")
puts "t23 ok"
