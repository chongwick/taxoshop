a = (1..4000).to_a
a.each_cons(2) { a.clear } rescue (puts "raised")
puts "e02 ok"
