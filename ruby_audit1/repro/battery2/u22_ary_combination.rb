a = (1..200).to_a
a.combination(2) { a.clear } rescue (puts "raised")
puts "u22 ok"
