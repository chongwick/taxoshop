a=(1..3000).to_a; a.min(5){|x,y| a.clear; x<=>y} rescue (puts "raised"); puts "n07 ok"
