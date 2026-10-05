a=(1..3000).to_a
a.combination(1){|x| a.clear} rescue (puts "raised"); puts "cb01 ok"
