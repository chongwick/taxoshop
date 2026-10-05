a=(1..3000).to_a; a.combination(2){ a.clear } rescue (puts "raised"); puts "b01 ok"
