a = (1..200).to_a
a.permutation(2) { a.clear } rescue (puts "raised")
puts "u23 ok"
