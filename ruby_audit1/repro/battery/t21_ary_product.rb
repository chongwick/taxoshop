a=(1..50).to_a; b=(1..50).to_a
a.product(b) { a.clear } rescue (puts "raised")
puts "t21 ok"
